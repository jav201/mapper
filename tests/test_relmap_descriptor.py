"""HLR-RML.1 / LLR-RML.1.1-.1.6 -- bounded repository reads and the relation descriptor.

`mapper/relmap/descriptor.py`: `read_repo_text` (lstat, identity, capped read), the closed causes
K1-K17 (`CAUSE`, read-only), the descriptor reader and schema, path confinement and discovery
(cap 8); `refusal_line` itself lives in the `text` leaf and is imported here.  This module is
also the in-process Layer A stand-in for AT-121/AT-127 (the
Layer B arms run `mapper --audit` and first exist at Inc-5, proposal 2.1 *Layer phasing*): it
asserts the exact refusal text each cause will print.

Heavy arms (the real 8 MiB cap, cap+1 with bytes-read instrumentation) are in their own functions
so a failure names the shape.  There is NO elapsed-time assertion.
"""
from __future__ import annotations

import builtins
import io
import os
import stat
import subprocess
import sys
import types
from pathlib import Path

import pytest

import mapper
from mapper import osopen
from mapper.osopen import MAX_MAP_BYTES, is_link
from mapper.relmap import descriptor as dmod
from mapper.relmap.descriptor import (
    CAUSE,
    Descriptor,
    DescriptorError,
    RepoReadError,
    default_descriptor,
    discover_descriptors,
    load_descriptor,
    read_repo_text,
)
from mapper.reqharness.derive import LIMIT_ROLES_YML_BYTES
from mapper.relmap.text import refusal_line

NAME = "r.relmap.yml"
CANON = "REQUIREMENTS.md"


def _write(root: Path, name: str, text: str | bytes) -> Path:
    path = root / name
    if isinstance(text, bytes):
        path.write_bytes(text)
    else:
        path.write_bytes(text.encode("utf-8"))
    return path


def _nested_flow(n: int) -> str:
    text = "0"
    for _ in range(n):
        text = "{k: " + text + "}"
    return text


def _padded(valid: str, size: int) -> bytes:
    """`valid` YAML followed by one comment line so the file is exactly `size` bytes."""
    base = valid.encode("utf-8")
    assert size > len(base) + 2
    return base + b"#" + b"p" * (size - len(base) - 1)


def _cause_of(call, *args):
    with pytest.raises((RepoReadError, DescriptorError)) as err:
        call(*args)
    return err.value


def _make_link(link: Path, target: Path) -> str:
    """A symlink, or on Windows a directory junction (`mklink /J`, no privilege); returns which.
    `blocked` (a hard failure, never a silent skip) only when neither can be created."""
    try:
        os.symlink(target, link, target_is_directory=target.is_dir())
        return "symlink"
    except (OSError, NotImplementedError):
        pass
    if sys.platform == "win32" and target.is_dir():
        done = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(target)],
                              capture_output=True, text=True, check=False)
        if done.returncode == 0 and link.exists():
            return "junction"
    pytest.fail("BLOCKED: neither a symlink nor a directory junction could be created here")


# ------------------------------------------------------------------ CAUSE (LLR-RML.1.1, M2)


def test_cause_table_is_k1_to_k17():
    assert list(CAUSE) == [f"K{i}" for i in range(1, 18)]
    assert len(set(CAUSE.values())) == 17
    assert CAUSE["K5"] == "exceeds the byte limit"
    assert CAUSE["K16"].format(key="us_canon") == "source.us_canon is not text"
    assert CAUSE["K17"].format(field="at_table", reason="outside") == "unsafe path in at_table (outside)"


def test_cause_is_read_only():
    assert isinstance(CAUSE, types.MappingProxyType)
    with pytest.raises(TypeError):
        CAUSE["K1"] = "rewritten"  # type: ignore[index]
    with pytest.raises(TypeError):
        del CAUSE["K1"]  # type: ignore[attr-defined]
    with pytest.raises(AttributeError):
        CAUSE.update({"K18": "x"})  # type: ignore[attr-defined]


# ------------------------------------------------------------------ read_repo_text (LLR-RML.1.5)


def test_read_repo_text_reads_a_plain_file(tmp_path):
    _write(tmp_path, CANON, "line one\r\nline two\n")
    assert read_repo_text(tmp_path / CANON, LIMIT_ROLES_YML_BYTES) == "line one\nline two\n"


def test_read_repo_text_missing_file_is_k3(tmp_path):
    err = _cause_of(read_repo_text, tmp_path / CANON, 100)
    assert (type(err), err.cause, err.limit) == (RepoReadError, CAUSE["K3"], 100)


def test_read_repo_text_directory_is_k2_and_is_never_opened(tmp_path, monkeypatch):
    (tmp_path / NAME).mkdir()

    def boom(*a, **k):
        raise AssertionError("a directory must be refused before any open")

    monkeypatch.setattr(os, "open", boom)
    monkeypatch.setattr(builtins, "open", boom)
    assert _cause_of(read_repo_text, tmp_path / NAME, 100).cause == CAUSE["K2"]


@pytest.mark.skipif(not hasattr(os, "mkfifo"), reason="n/a - Windows has no mkfifo")
def test_read_repo_text_fifo_is_k2_and_is_never_opened(tmp_path, monkeypatch):
    fifo = tmp_path / "pipe.relmap.yml"
    os.mkfifo(fifo)
    monkeypatch.setattr(os, "open", lambda *a, **k: pytest.fail("a FIFO must not be opened"))
    assert _cause_of(read_repo_text, fifo, 100).cause == CAUSE["K2"]


def test_read_repo_text_link_is_k1_and_is_never_opened(tmp_path, monkeypatch):
    """K1.  A symlink where this machine allows one, else a Windows directory junction (D-8)."""
    target = tmp_path / "target"
    target.mkdir()
    link = tmp_path / NAME
    how = _make_link(link, target)
    assert is_link(os.lstat(link)), how  # the thing created really is what `osopen.is_link` is meant to catch
    monkeypatch.setattr(os, "open", lambda *a, **k: pytest.fail("a link must be refused before any open"))
    monkeypatch.setattr(builtins, "open", lambda *a, **k: pytest.fail("a link must be refused before any open"))
    assert _cause_of(read_repo_text, link, 100).cause == CAUSE["K1"]


def test_read_repo_text_file_symlink_is_k1(tmp_path):
    real = _write(tmp_path, "real.txt", "x: 1\n")
    link = tmp_path / NAME
    try:
        os.symlink(real, link)
    except (OSError, NotImplementedError):
        pytest.skip("n/a - a file symlink needs a privilege this account lacks; the junction arm covers K1")
    assert _cause_of(read_repo_text, link, 100).cause == CAUSE["K1"]


@pytest.mark.skipif(sys.platform != "win32", reason="n/a - a junction is a Windows reparse point")
def test_read_repo_text_windows_junction_is_a_reparse_point_is_link_catches(tmp_path):
    target = tmp_path / "t"
    target.mkdir()
    junction = tmp_path / "j.relmap.yml"
    done = subprocess.run(["cmd", "/c", "mklink", "/J", str(junction), str(target)],
                          capture_output=True, text=True, check=False)
    if done.returncode != 0:
        pytest.fail("BLOCKED: the directory junction could not be created: " + done.stderr.strip())
    info = os.lstat(junction)
    assert info.st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT
    assert is_link(info), "a junction that osopen.is_link misses is itself a finding"
    assert _cause_of(read_repo_text, junction, 100).cause == CAUSE["K1"]
    assert _cause_of(load_descriptor, junction, tmp_path).cause == CAUSE["K1"]


def test_read_repo_text_a_hard_linked_regular_file_is_read(tmp_path):
    real = _write(tmp_path, "real.txt", "hello\n")
    twin = tmp_path / "twin.txt"
    try:
        os.link(real, twin)
    except (OSError, NotImplementedError):
        pytest.skip("n/a - hard links unavailable on this filesystem")
    assert os.lstat(twin).st_nlink > 1
    assert read_repo_text(twin, 100) == "hello\n"


def test_read_repo_text_cannot_open_is_k4(tmp_path, monkeypatch):
    _write(tmp_path, CANON, "x\n")

    def denied(*a, **k):
        raise PermissionError("denied: C:\\private\\path")

    monkeypatch.setattr(dmod.os, "open", denied)
    err = _cause_of(read_repo_text, tmp_path / CANON, 100)
    assert err.cause == CAUSE["K4"]
    assert "private" not in str(err)


def test_read_repo_text_unclassified_oserror_from_the_reader_is_k4(tmp_path, monkeypatch):
    _write(tmp_path, CANON, "x\n")

    def broken(path, cap):
        raise OSError("C:\\private\\detail")

    monkeypatch.setattr(dmod, "read_capped", broken)
    err = _cause_of(read_repo_text, tmp_path / CANON, 100)
    assert err.cause == CAUSE["K4"] and "private" not in str(err)


def test_read_repo_text_nul_is_k6_and_invalid_utf8_is_k7(tmp_path):
    _write(tmp_path, "nul.txt", b"a: 1\x00\n")
    _write(tmp_path, "bad.txt", b"a: \xff\xfe\n")
    assert _cause_of(read_repo_text, tmp_path / "nul.txt", 100).cause == CAUSE["K6"]
    assert _cause_of(read_repo_text, tmp_path / "bad.txt", 100).cause == CAUSE["K7"]


@pytest.mark.parametrize("cap", [LIMIT_ROLES_YML_BYTES, MAX_MAP_BYTES], ids=["canon-cap", "descriptor-cap"])
def test_read_repo_text_cap_plus_minus_one_for_both_caps(tmp_path, cap):
    """Both caps the package passes, at the real constants.  Comment-padded text, because a
    zero-filled file is refused as binary by the NUL probe before the cap matters."""
    at_cap = _write(tmp_path, "at.txt", b"#" * cap)
    assert len(read_repo_text(at_cap, cap)) == cap
    over = _write(tmp_path, "over.txt", b"#" * (cap + 1))
    err = _cause_of(read_repo_text, over, cap)
    assert (err.cause, err.limit) == (CAUSE["K5"], cap)


def test_the_canon_cap_is_the_one_load_canon_enforced():
    from mapper.reqharness import derive
    assert derive.LIMIT_ROLES_YML_BYTES == LIMIT_ROLES_YML_BYTES
    assert MAX_MAP_BYTES == 8 * 1024 * 1024


class _Tally:
    """Counts the bytes handed back by every read of one target, through every door this process
    offers: `open`, `io.open`, `os.open` + `os.read`.  A mutant that reads the whole file and
    only then compares raises the same K5 text, so the result alone cannot tell it apart."""

    def __init__(self, target: Path):
        self.target = str(target)
        self.bytes = 0
        self.fds: set[int] = set()

    def install(self, monkeypatch):
        real_open, real_os_open, real_os_read = builtins.open, os.open, os.read
        tally = self

        class Counting:
            def __init__(self, handle):
                self._h = handle

            def read(self, *a):
                data = self._h.read(*a)
                tally.bytes += len(data)
                return data

            def __getattr__(self, name):
                return getattr(self._h, name)

            def __enter__(self):
                self._h.__enter__()
                return self

            def __exit__(self, *exc):
                return self._h.__exit__(*exc)

            def __iter__(self):
                return iter(self._h)

        def counting_open(file, *a, **k):
            handle = real_open(file, *a, **k)
            return Counting(handle) if str(file) == tally.target else handle

        def counting_os_open(path, *a, **k):
            fd = real_os_open(path, *a, **k)
            if str(path) == tally.target:
                tally.fds.add(fd)
            return fd

        def counting_os_read(fd, n):
            data = real_os_read(fd, n)
            if fd in tally.fds:
                tally.bytes += len(data)
            return data

        monkeypatch.setattr(builtins, "open", counting_open)
        monkeypatch.setattr(io, "open", counting_open)
        monkeypatch.setattr(os, "open", counting_os_open)
        monkeypatch.setattr(os, "read", counting_os_read)


def test_tally_instrument_can_report_a_whole_file_read(tmp_path, monkeypatch):
    """RED-proof of the instrument: reading the file whole through each door registers."""
    path = _write(tmp_path, "t.bin", b"x" * 5000)
    tally = _Tally(path)
    tally.install(monkeypatch)
    path.read_bytes()
    with open(path, "rb") as handle:
        handle.read()
    fd = os.open(path, os.O_RDONLY | getattr(os, "O_BINARY", 0))
    os.read(fd, 5000)
    os.close(fd)
    assert tally.bytes == 15000


def test_read_repo_text_cap_plus_one_reads_at_most_cap_plus_one_bytes(tmp_path, monkeypatch):
    """M-RML-8.  A file one byte over the cap is refused AND the read never takes more than
    cap + 1 bytes (small cap here: the bound is the property, not the constant)."""
    cap = 4096
    path = _write(tmp_path, NAME, b"#" * (cap + 1))
    tally = _Tally(path)
    tally.install(monkeypatch)
    err = _cause_of(read_repo_text, path, cap)
    assert err.cause == CAUSE["K5"]
    assert tally.bytes <= cap + 1, tally.bytes


def test_read_repo_text_far_over_the_cap_is_never_read_whole(tmp_path, monkeypatch):
    """M-RML-8, the shape that separates the mutants: a file far past the cap.  A reader that reads
    the whole file first and compares afterwards takes every byte; the real one takes at most cap + 1."""
    cap = 4096
    path = _write(tmp_path, NAME, b"#" * (cap * 50))
    tally = _Tally(path)
    tally.install(monkeypatch)
    assert _cause_of(read_repo_text, path, cap).cause == CAUSE["K5"]
    assert tally.bytes <= cap + 1, tally.bytes


def _fake_stat(real, **changes):
    values = dict(st_mode=real.st_mode, st_dev=real.st_dev, st_ino=real.st_ino,
                  st_file_attributes=getattr(real, "st_file_attributes", 0))
    values.update(changes)
    return types.SimpleNamespace(**values)


def _patch_fstat(monkeypatch, path: Path, **changes):
    real_fstat = os.fstat
    fds: set[int] = set()
    real_os_open = os.open

    def tracking_open(p, *a, **k):
        fd = real_os_open(p, *a, **k)
        if str(p) == str(path):
            fds.add(fd)
        return fd

    def fake_fstat(fd):
        real = real_fstat(fd)
        return _fake_stat(real, **changes) if fd in fds else real

    monkeypatch.setattr(dmod.os, "open", tracking_open)
    monkeypatch.setattr(dmod.os, "fstat", fake_fstat)


def test_read_repo_text_identity_mismatch_is_k2(tmp_path, monkeypatch):
    """M-RML-14: the opened file is not the file lstat described (another inode)."""
    path = _write(tmp_path, NAME, "kind: relation\n")
    _patch_fstat(monkeypatch, path, st_ino=os.lstat(path).st_ino + 1)
    assert _cause_of(read_repo_text, path, 1000).cause == CAUSE["K2"]


def test_read_repo_text_device_mismatch_is_k2(tmp_path, monkeypatch):
    path = _write(tmp_path, NAME, "kind: relation\n")
    _patch_fstat(monkeypatch, path, st_dev=os.lstat(path).st_dev + 1)
    assert _cause_of(read_repo_text, path, 1000).cause == CAUSE["K2"]


def test_read_repo_text_opened_file_not_regular_is_k2(tmp_path, monkeypatch):
    path = _write(tmp_path, NAME, "kind: relation\n")
    _patch_fstat(monkeypatch, path, st_mode=stat.S_IFDIR | 0o755)
    assert _cause_of(read_repo_text, path, 1000).cause == CAUSE["K2"]


def test_read_repo_text_inode_zero_on_both_sides_is_read(tmp_path, monkeypatch):
    """M1 / M-RML-16: some network and FAT mounts report st_ino = 0; refusing would refuse every file there."""
    path = _write(tmp_path, NAME, "kind: relation\n")
    real_lstat = os.lstat

    def zero_lstat(p, *a, **k):
        real = real_lstat(p, *a, **k)
        return _fake_stat(real, st_ino=0) if str(p) == str(path) else real

    monkeypatch.setattr(dmod.os, "lstat", zero_lstat)
    _patch_fstat(monkeypatch, path, st_ino=0)
    assert read_repo_text(path, 1000) == "kind: relation\n"


def test_read_repo_text_inode_zero_on_one_side_only_is_read(tmp_path, monkeypatch):
    path = _write(tmp_path, NAME, "kind: relation\n")
    _patch_fstat(monkeypatch, path, st_ino=0)
    assert read_repo_text(path, 1000) == "kind: relation\n"


def test_read_repo_text_the_opened_descriptor_is_closed(tmp_path, monkeypatch):
    path = _write(tmp_path, NAME, "kind: relation\n")
    opened, closed = [], []
    real_open, real_close = os.open, os.close

    def tracking_open(p, *a, **k):
        fd = real_open(p, *a, **k)
        opened.append(fd)
        return fd

    def tracking_close(fd):
        closed.append(fd)
        real_close(fd)

    monkeypatch.setattr(dmod.os, "open", tracking_open)
    monkeypatch.setattr(dmod.os, "close", tracking_close)
    read_repo_text(path, 1000)
    assert opened and set(opened) <= set(closed)


# ------------------------------------------------------------------ load_descriptor (LLR-RML.1.1)


def test_load_descriptor_read_causes_carry_the_base_name_only(tmp_path):
    secret = tmp_path / "PRIVATE-MARKER"
    secret.mkdir()
    missing = secret / NAME
    err = _cause_of(load_descriptor, missing, tmp_path)
    assert (type(err), err.cause, err.name) == (DescriptorError, CAUSE["K3"], NAME)
    assert str(err) == f"{NAME}: {CAUSE['K3']}"
    assert "PRIVATE-MARKER" not in str(err) and str(tmp_path) not in str(err)


def test_k1_k2_via_load_descriptor(tmp_path):
    (tmp_path / "d.relmap.yml").mkdir()
    assert _cause_of(load_descriptor, tmp_path / "d.relmap.yml", tmp_path).cause == CAUSE["K2"]
    target = tmp_path / "t"
    target.mkdir()
    link = tmp_path / "l.relmap.yml"
    _make_link(link, target)
    assert _cause_of(load_descriptor, link, tmp_path).cause == CAUSE["K1"]


def test_k6_k7_via_load_descriptor(tmp_path):
    p = _write(tmp_path, "nul.relmap.yml", b"kind: relation\x00\n")
    q = _write(tmp_path, "bad.relmap.yml", b"kind: \xff\xfe\n")
    assert _cause_of(load_descriptor, p, tmp_path).cause == CAUSE["K6"]
    assert _cause_of(load_descriptor, q, tmp_path).cause == CAUSE["K7"]


def test_k8_anchor_and_alias_name_nothing(tmp_path):
    for text in ("a: &SECRETANCHOR 1\nb: *SECRETANCHOR\n", "b: *OTHERALIAS\n"):
        err = _cause_of(load_descriptor, _write(tmp_path, NAME, text), tmp_path)
        assert err.cause == CAUSE["K8"]
        assert "SECRET" not in str(err) and "OTHER" not in str(err)


def test_k9_depth_65_refused_and_depth_64_loads(tmp_path):
    loads = load_descriptor(_write(tmp_path, NAME, "x: " + _nested_flow(63) + "\n"), tmp_path)
    assert isinstance(loads, Descriptor) and loads.ignored_keys == ("x",)
    err = _cause_of(load_descriptor, _write(tmp_path, NAME, "x: " + _nested_flow(64) + "\n"), tmp_path)
    assert err.cause == CAUSE["K9"]


def test_k10_not_valid_yaml_prints_only_the_cause(tmp_path):
    hostile = "a: [HOSTILE-SNIPPET-\x1b[31m-" + "z" * 50 + "\n"
    big_int = "a: " + "9" * 5000 + "\n"
    multi_doc = "a: 1\n---\nb: 2\n"
    unhashable = "? [1, 2]\n: v\n"
    tab = "a:\n\t- b\n"
    for text in (hostile, "a: [\n", big_int, multi_doc, unhashable, tab):
        err = _cause_of(load_descriptor, _write(tmp_path, NAME, text), tmp_path)
        assert err.cause == CAUSE["K10"], text[:30]
        assert str(err) == f"{NAME}: {CAUSE['K10']}"
        assert "HOSTILE" not in str(err) and "\x1b" not in str(err)


def test_a_syntax_error_in_the_prescan_is_k10_not_a_crash(tmp_path):
    """M-RML-15: `a: [` fails inside `yaml.parse` (the prescan), so the net must cover the prescan too."""
    assert _cause_of(load_descriptor, _write(tmp_path, NAME, "a: [\n"), tmp_path).cause == CAUSE["K10"]


def test_the_prescan_runs_before_safe_load(tmp_path, monkeypatch):
    """M-RML-1: an anchor-amplified document must be refused before `safe_load` can compose it."""
    def forbidden(*a, **k):
        raise AssertionError("safe_load ran on a document the prescan should have refused")

    monkeypatch.setattr(dmod.yaml, "safe_load", forbidden)
    err = _cause_of(load_descriptor, _write(tmp_path, NAME, "a: &x [1]\nb: *x\n"), tmp_path)
    assert err.cause == CAUSE["K8"]


def test_a_utf8_bom_before_valid_yaml_loads(tmp_path):
    got = load_descriptor(_write(tmp_path, NAME, b"\xef\xbb\xbfkind: relation\n"), tmp_path)
    assert got == default_descriptor()


def test_the_descriptor_read_goes_through_read_repo_text(tmp_path, monkeypatch):
    seen = []

    def spy(path, cap):
        seen.append((Path(path).name, cap))
        return "{}\n"

    monkeypatch.setattr(dmod, "read_repo_text", spy)
    load_descriptor(tmp_path / NAME, tmp_path)
    assert seen == [(NAME, MAX_MAP_BYTES)]


# ------------------------------------------------------------------ schema (LLR-RML.1.2)


@pytest.mark.parametrize(
    "text,key",
    [
        ("", "K11"), ("# nothing but a comment\n", "K11"), ("- a\n- b\n", "K11"), ("just text\n", "K11"),
        ("kind: graph\n", "K12"), ("kind: [1]\n", "K12"), ("kind: 7\n", "K12"), ("kind:\n", "K12"),
        ("profile: lineage\n", "K13"), ("profile: [x]\n", "K13"), ("profile: {a: b}\n", "K13"),
        ("profile: 3\n", "K13"), ("profile:\n", "K13"),
        ("source: [1]\n", "K15"), ("source: text\n", "K15"), ("source:\n", "K15"),
        ("source: {canon: OTHER.md}\n", "K14"), ("source: {canon: [REQUIREMENTS.md]}\n", "K14"),
    ],
)
def test_schema_table_refusals(tmp_path, text, key):
    err = _cause_of(load_descriptor, _write(tmp_path, NAME, text), tmp_path)
    assert err.cause == CAUSE[key], (text, err.cause)


@pytest.mark.parametrize("field", ["us_canon", "at_table"])
@pytest.mark.parametrize("value", ["[a]", "5", "{a: b}", "true", "null"])
def test_schema_table_k16_names_the_key_not_the_value(tmp_path, field, value):
    err = _cause_of(load_descriptor, _write(tmp_path, NAME, f"source:\n  {field}: {value}\n"), tmp_path)
    assert err.cause == f"source.{field} is not text"


def test_schema_table_accepts(tmp_path):
    assert load_descriptor(_write(tmp_path, NAME, "{}\n"), tmp_path) == default_descriptor()
    assert load_descriptor(_write(tmp_path, NAME, "kind: relation\nprofile: reqharness\n"), tmp_path) == default_descriptor()
    assert load_descriptor(_write(tmp_path, NAME, "source: {}\n"), tmp_path) == default_descriptor()
    assert load_descriptor(_write(tmp_path, NAME, "source: {canon: REQUIREMENTS.md}\n"), tmp_path) == default_descriptor()
    full = load_descriptor(
        _write(tmp_path, NAME, "source:\n  us_canon: docs/us.md\n  at_table: docs/at.md\n"), tmp_path)
    assert (full.us_canon, full.at_table, full.profile, full.canon) == ("docs/us.md", "docs/at.md", "reqharness", "REQUIREMENTS.md")


def test_default_descriptor_row():
    assert default_descriptor() == Descriptor("reqharness", "REQUIREMENTS.md", None, None, ())


def test_unknown_top_level_keys_are_kept_as_notes_never_errors(tmp_path):
    long_key = "k" * 300
    got = load_descriptor(
        _write(tmp_path, NAME, f"kind: relation\nflavour: mint\n7: seven\n{long_key}: x\n"), tmp_path)
    assert got.ignored_keys[:2] == ("flavour", "7")
    assert len(got.ignored_keys[2]) == 120 and got.ignored_keys[2].endswith("…")


def test_the_lineage_profile_is_refused_until_r5(tmp_path):
    """M-RML-3: accepting `lineage` would hand the adapter a profile it cannot build."""
    assert _cause_of(load_descriptor, _write(tmp_path, NAME, "profile: lineage\n"), tmp_path).cause == CAUSE["K13"]


# ------------------------------------------------------------------ paths (LLR-RML.1.3)


def test_paths_confined(tmp_path):
    unsafe = {
        "absolute": str(Path(tmp_path.anchor) / "Windows" / "x.md") if sys.platform == "win32" else "/etc/passwd",
        "unc": "\\\\server\\share\\x.md",
        "dotdot": "../outside.md",
        "device": "CON",
        "home": "~/x",
        "drive": "C:x.md",
    }
    reasons = {"allow_list", "colon", "normalised", "outside", "link", "unreadable"}
    for label, value in unsafe.items():
        quoted = "'" + value.replace("'", "''") + "'"
        err = _cause_of(load_descriptor, _write(tmp_path, NAME, f"source:\n  us_canon: {quoted}\n"), tmp_path)
        assert err.cause.startswith("unsafe path in us_canon ("), (label, err.cause)
        assert err.cause[len("unsafe path in us_canon ("):-1] in reasons, (label, err.cause)
        assert value not in str(err), label
    assert load_descriptor(_write(tmp_path, NAME, "source:\n  at_table: docs/at.md\n"), tmp_path).at_table == "docs/at.md"
    home = _cause_of(load_descriptor, _write(tmp_path, NAME, "source:\n  us_canon: ~/x\n"), tmp_path)
    assert home.cause == "unsafe path in us_canon (outside)"


def test_paths_confined_names_the_field(tmp_path):
    err = _cause_of(load_descriptor, _write(tmp_path, NAME, "source:\n  at_table: ../x\n"), tmp_path)
    assert err.cause.startswith("unsafe path in at_table (")


def test_a_link_inside_the_repository_is_a_k17_link(tmp_path):
    outside = tmp_path / "outside"
    outside.mkdir()
    repo = tmp_path / "repo"
    repo.mkdir()
    _make_link(repo / "hop", outside)
    err = _cause_of(load_descriptor, _write(repo, NAME, "source:\n  us_canon: hop/x.md\n"), repo)
    assert err.cause == "unsafe path in us_canon (link)"


def test_a_unc_string_causes_no_open_and_no_stat_for_that_string(tmp_path, monkeypatch):
    """LLR-RML.1.3: confinement works on the text; the configured path is never opened or stat-ed."""
    marker = "UNC-MARKER-SERVER"
    path = _write(tmp_path, NAME, f"source:\n  us_canon: '\\\\{marker}\\share\\x.md'\n")
    real_open, real_stat, real_lstat, real_os_open = builtins.open, os.stat, os.lstat, os.open

    def guard(real):
        def wrapped(p, *a, **k):
            if marker in str(p):
                raise AssertionError(f"the configured string reached the filesystem: {p}")
            return real(p, *a, **k)
        return wrapped

    monkeypatch.setattr(builtins, "open", guard(real_open))
    monkeypatch.setattr(os, "stat", guard(real_stat))
    monkeypatch.setattr(os, "lstat", guard(real_lstat))
    monkeypatch.setattr(os, "open", guard(real_os_open))
    err = _cause_of(load_descriptor, path, tmp_path)
    assert err.cause.startswith("unsafe path in us_canon (")


def test_configured_paths_are_never_opened_in_r1(tmp_path, monkeypatch):
    """R1 confines `us_canon` / `at_table` and reads neither: only the descriptor itself is opened."""
    (tmp_path / "docs").mkdir()
    _write(tmp_path / "docs", "us.md", "x\n")
    path = _write(tmp_path, NAME, "source:\n  us_canon: docs/us.md\n")
    opened = []
    real = os.open

    def spy(p, *a, **k):
        opened.append(Path(p).name)
        return real(p, *a, **k)

    monkeypatch.setattr(dmod.os, "open", spy)
    load_descriptor(path, tmp_path)
    assert opened == [NAME]


# ------------------------------------------------------------------ cap +/- 1 on the real constant


def test_descriptor_at_cap_minus_one_loads_and_at_cap_plus_one_is_k5(tmp_path):
    """Heavy arm: the real 8 MiB constant, comment-padded VALID YAML (never a monkeypatched cap)."""
    loads = _write(tmp_path, "a.relmap.yml", _padded("kind: relation\n", MAX_MAP_BYTES - 1))
    assert os.path.getsize(loads) == MAX_MAP_BYTES - 1
    assert load_descriptor(loads, tmp_path) == default_descriptor()
    over = _write(tmp_path, "b.relmap.yml", _padded("kind: relation\n", MAX_MAP_BYTES + 1))
    err = _cause_of(load_descriptor, over, tmp_path)
    assert (err.cause, err.limit, err.name) == (CAUSE["K5"], MAX_MAP_BYTES, "b.relmap.yml")


def test_a_zero_filled_file_is_binary_not_a_cap_arm(tmp_path):
    zeros = _write(tmp_path, NAME, b"\x00" * 1024)
    assert _cause_of(load_descriptor, zeros, tmp_path).cause == CAUSE["K6"]


# ------------------------------------------------------------------ refusal_line (M4)


def test_refusal_line_form_and_k5_rendering():
    assert refusal_line("a.relmap.yml", CAUSE["K1"]) == "structure: refused (a.relmap.yml): is a link - descriptor skipped"
    assert refusal_line("a.relmap.yml", CAUSE["K5"], MAX_MAP_BYTES) == (
        f"structure: refused (a.relmap.yml): exceeds the {MAX_MAP_BYTES} byte limit - descriptor skipped")
    assert "exceeds the byte limit" in refusal_line("a.relmap.yml", CAUSE["K5"])
    assert refusal_line("a", CAUSE["K16"].format(key="at_table")) == (
        "structure: refused (a): source.at_table is not text - descriptor skipped")


@pytest.mark.parametrize("name", ["e\u0301" + "x" * 5, "n" * 300, "\u0301" * 300, "z" * 120, "z" * 121])
def test_refusal_line_hostile_base_name_is_cut_to_120(name):
    line = refusal_line(name, CAUSE["K10"])
    shown = line[len("structure: refused ("):line.index("): " + CAUSE["K10"])]
    assert len(shown) <= 120
    if len(name) > 120:
        assert len(shown) == 120 and shown.endswith("…")
    else:
        assert shown == name
    assert line.endswith(": not valid YAML - descriptor skipped")


# ------------------------------------------------------------------ discovery (LLR-RML.1.6)


def _repo_with(tmp_path, names):
    for n in names:
        _write(tmp_path, n, "kind: relation\n")
    return tmp_path


@pytest.mark.parametrize("count", [0, 1, 2, 8, 9])
def test_repo_root_census_counts(tmp_path, count):
    names = [f"{chr(ord('a') + i)}.relmap.yml" for i in range(count)]
    _repo_with(tmp_path, reversed(names))
    paths, overflow = discover_descriptors(tmp_path)
    assert [p.name for p in paths] == names[:8]
    assert overflow == max(0, count - 8)
    assert all(p.parent == tmp_path for p in paths)


def test_repo_root_census_sorted_by_code_point_and_case_sensitive(tmp_path):
    _repo_with(tmp_path, ["b.relmap.yml", "M.relmap.yml", "a.relmap.yml", "Z.relmap.yml",
                          "c.RELMAP.YML", "d.relmap.yaml", "e.relmap.yml.bak", "relmap.yml", "f.yml"])
    paths, overflow = discover_descriptors(tmp_path)
    assert [p.name for p in paths] == ["M.relmap.yml", "Z.relmap.yml", "a.relmap.yml", "b.relmap.yml"]
    assert overflow == 0


def test_repo_root_census_lists_non_regular_entries_so_reading_refuses_them(tmp_path):
    (tmp_path / "x.relmap.yml").mkdir()
    target = tmp_path / "t"
    target.mkdir()
    _make_link(tmp_path / "y.relmap.yml", target)
    _write(tmp_path, "z.relmap.yml", "{}\n")
    paths, overflow = discover_descriptors(tmp_path)
    assert [p.name for p in paths] == ["x.relmap.yml", "y.relmap.yml", "z.relmap.yml"]
    causes = {p.name: _cause_of(load_descriptor, p, tmp_path).cause for p in paths[:2]}
    assert causes == {"x.relmap.yml": CAUSE["K2"], "y.relmap.yml": CAUSE["K1"]}
    assert load_descriptor(paths[2], tmp_path) == default_descriptor()


def test_repo_root_census_does_not_descend(tmp_path):
    (tmp_path / "sub").mkdir()
    _write(tmp_path / "sub", "deep.relmap.yml", "{}\n")
    assert discover_descriptors(tmp_path) == ((), 0)


def test_discovery_of_an_unlistable_root_is_empty_not_a_crash(tmp_path):
    assert discover_descriptors(tmp_path / "missing") == ((), 0)


def test_the_input_class_is_new_no_test_fixture_or_tracked_file_carries_it():
    """Census by CONTENT (the hygiene batch's B1 miss): no existing suite writes a root-level
    `*.relmap.yml` that the new reader would now trip over.  Only the relmap descriptor suites
    name the suffix."""
    tests_dir = Path(mapper.__file__).resolve().parent.parent / "tests"
    mine = {"test_relmap_descriptor.py", "test_relmap_isolation.py", "test_relmap_audit.py",  # audit: Inc-5 Layer B fixtures
            "test_relmap_text.py",  # R2 Inc-1a: the presentation-leaf refusal battery names base names
            "test_relmap_shell.py"}  # R2 Inc-2: the host's hostile-descriptor arm seeds a `*.relmap.yml`
    hits = {p.name for p in tests_dir.rglob("*.py") if ".relmap.yml" in p.read_text(encoding="utf-8")}
    assert hits <= mine, hits - mine
    root = Path(mapper.__file__).resolve().parent.parent
    found = []
    for here, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in {".git", ".dev-flow", "node_modules", "__pycache__"}]
        found += [os.path.join(here, f) for f in files if f.endswith(".relmap.yml")]
    assert found == [], found
