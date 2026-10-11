"""HLR-RH.1 / LLR-RH.1.1–1.4 — config schema, genesis, canonical form, email hashing.

The four node names are the executed verification named in
`.dev-flow/2026-10-11-reqharness-batch/01-requirements.md` §3/§4 for HLR-RH.1.
Every refusal is asserted by NAME (R9); the canonical-form arms pin the
`{"a": "ab", "b": "c"}` vs `{"a": "a", "b": "bc"}` field-boundary pair (R3).
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

import pytest

from mapper.reqharness.canonical import (
    NfcKeyCollision,
    canonical_digest,
    canonical_json,
    nfc,
)
from mapper.reqharness.config import (
    GENESIS_NOTE,
    GENESIS_PREV,
    LIMIT_NESTING_DEPTH,
    RegistryExistsError,
    check_int,
    check_time,
    config_digest,
    create_registry,
    email_sha256,
    load_config,
    load_documents,
)
from mapper.reqharness.records import ValidationError

NOW = "2026-10-11T09:00:00Z"

VALID_CONFIG = """\
version: "1"
people:
- id: ana
  name: Ana Reviewer
  email_sha256: "6d1d4b6e8d6b3a4a8b2c4f1a9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b3a2f1e0d"
roles:
- id: admin
- id: req-reviewer
classes:
- id: HLR
  reviewer_role: req-reviewer
  normative_fields: [statement]
  informative_fields: [rationale]
- id: LLR
  reviewer_role: req-reviewer
  normative_fields: [statement]
  informative_fields: []
release_rules:
- id: all_active_reviewed
"""

CLEAR_EMAIL_RE = re.compile(rb"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


def _write_config(tmp_path: Path, text: str) -> Path:
    target = tmp_path / "reqharness"
    target.mkdir(exist_ok=True)
    (target / "config.yml").write_text(text, encoding="utf-8")
    return tmp_path


def test_load_rejects_unknown_reviewer_role(tmp_path):
    """LLR-RH.1.1: the reviewer-role cross-check names class AND role; the
    typed schema refuses unknown keys, missing keys, non-`str` scalars
    (datetime / bool / empty shapes — R18), normative/informative overlap,
    anchors/aliases and duplicate keys (R21) — each refusal named, and a
    valid fixture round-trips."""
    bad_role = VALID_CONFIG.replace("reviewer_role: req-reviewer", "reviewer_role: nosuch", 1)
    _write_config(tmp_path, bad_role)
    with pytest.raises(ValidationError, match=r"class=HLR role=nosuch"):
        load_config(tmp_path)

    overlap = VALID_CONFIG.replace("informative_fields: [rationale]", "informative_fields: [rationale, statement]", 1)
    _write_config(tmp_path, overlap)
    with pytest.raises(ValidationError, match=r"class=HLR normative/informative overlap"):
        load_config(tmp_path)

    unknown_key = VALID_CONFIG.replace("release_rules:", "surplus: x\nrelease_rules:")
    _write_config(tmp_path, unknown_key)
    with pytest.raises(ValidationError, match=r"unknown key\(s\): surplus"):
        load_config(tmp_path)

    missing_key = VALID_CONFIG.replace("release_rules:\n- id: all_active_reviewed\n", "")
    _write_config(tmp_path, missing_key)
    with pytest.raises(ValidationError, match=r"missing key\(s\): release_rules"):
        load_config(tmp_path)

    anchored = "&x version: \"1\"\n"
    _write_config(tmp_path, anchored)
    with pytest.raises(ValidationError, match=r"anchors and aliases are not allowed"):
        load_config(tmp_path)

    aliased = VALID_CONFIG.replace('version: "1"', "base: &b \"1\"\nversion: *b")
    _write_config(tmp_path, aliased)
    with pytest.raises(ValidationError, match=r"anchors and aliases are not allowed"):
        load_config(tmp_path)

    duplicate = VALID_CONFIG + 'roles:\n- id: admin\n'
    _write_config(tmp_path, duplicate)
    with pytest.raises(ValidationError, match=r"duplicate key"):
        load_config(tmp_path)

    malformed = "version: \"1\"\npeople: [unclosed\n"
    _write_config(tmp_path, malformed)
    with pytest.raises(ValidationError, match=r"malformed YAML"):
        load_config(tmp_path)

    # K3 re-check LOW-4: config.yml carries the SAME named 64 KB cap as the
    # event files (LIMIT_EVENT_FILE_BYTES) — refused by name, bytes counted,
    # before any parse; a file one byte under the cap still loads
    from mapper.reqharness.config import LIMIT_EVENT_FILE_BYTES

    pad = "A" * (LIMIT_EVENT_FILE_BYTES + 16)
    _write_config(tmp_path, VALID_CONFIG.replace("name: Ana Reviewer", f"name: {pad}"))
    with pytest.raises(ValidationError) as excinfo:
        load_config(tmp_path)
    message = str(excinfo.value)
    assert message.startswith("reqharness/config.yml: file too large (")
    assert f"> {LIMIT_EVENT_FILE_BYTES} byte limit" in message

    under = "B" * (LIMIT_EVENT_FILE_BYTES - len(VALID_CONFIG) - 16)
    _write_config(tmp_path, VALID_CONFIG.replace("name: Ana Reviewer", f"name: {under}"))
    config = load_config(tmp_path)
    assert config.version == "1"

    datetime_shaped = VALID_CONFIG.replace("name: Ana Reviewer", "name: 2026-10-11T09:00:00Z")
    _write_config(tmp_path, datetime_shaped)
    with pytest.raises(ValidationError, match=r"field 'people\[0\].name' must be a str"):
        load_config(tmp_path)

    bool_shaped = VALID_CONFIG.replace("name: Ana Reviewer", "name: no")
    _write_config(tmp_path, bool_shaped)
    with pytest.raises(ValidationError, match=r"field 'people\[0\].name' must be a str"):
        load_config(tmp_path)

    empty_shaped = VALID_CONFIG.replace("name: Ana Reviewer", "name:")
    _write_config(tmp_path, empty_shaped)
    with pytest.raises(ValidationError, match=r"field 'people\[0\].name' must be a str"):
        load_config(tmp_path)

    _write_config(tmp_path, VALID_CONFIG)
    config = load_config(tmp_path)
    assert config.version == "1"
    assert [p.id for p in config.people] == ["ana"]
    assert config.roles == ("admin", "req-reviewer")
    hlr = next(c for c in config.classes if c.id == "HLR")
    assert hlr.reviewer_role == "req-reviewer"
    assert hlr.normative_fields == ("statement",)
    assert hlr.informative_fields == ("rationale",)
    assert [r.id for r in config.release_rules] == ["all_active_reviewed"]


def test_genesis_creates_chain_with_declared_admin(tmp_path):
    """LLR-RH.1.2: a fresh registry is policy-bound from the first document
    (R15) — genesis records `roles_hash: "GENESIS"` (no self-reference) and
    `config_hash` = sha256(canonical config at creation), and its `this_hash`
    verifies by the chain-link recomputation.  A malformed `now` is refused
    by the exact time format (R18)."""
    config = create_registry(
        tmp_path, person="bob", name="Bob Admin", email="bob@example.invalid", now=NOW
    )
    assert config.roles == ("admin", "req-reviewer")
    roles_path = tmp_path / "reqharness" / "roles.yml"
    assert roles_path.is_file()
    (document,) = load_documents(roles_path.read_text(encoding="utf-8"), where="roles.yml")
    assert document["action"] == "genesis"
    assert document["approved_by"] == "genesis"
    assert document["requested_by"] == "bob"
    assert document["person"] == "bob"
    assert document["role"] == "admin"
    assert document["note"] == GENESIS_NOTE
    assert document["seq"] == 1
    assert isinstance(document["seq"], int)
    assert document["roles_seq"] == 1
    assert document["prev_hash"] == GENESIS_PREV
    assert document["roles_hash"] == GENESIS_PREV  # NO self-reference

    # The creation-time config hash binds the registry (a genesis without it
    # fails — mutation M-CF1's arm), and it equals the canonical digest of
    # the config as LOADED back from disk.
    assert document["config_hash"] == config_digest(load_config(tmp_path))

    # The genesis link verifies: sha256(prev_hash + "\n" + canonical(event
    # without this_hash)) — recomputed here independently of the writer.
    event = {k: v for k, v in document.items() if k != "this_hash"}
    expected = hashlib.sha256(
        (GENESIS_PREV + "\n" + canonical_json(event)).encode("utf-8")
    ).hexdigest()
    assert document["this_hash"] == expected
    assert re.fullmatch(r"[0-9a-f]{64}", document["this_hash"])

    with pytest.raises(ValidationError, match=r"YYYY-MM-DDTHH:MM:SSZ"):
        create_registry(
            tmp_path / "bad",
            person="bob",
            name="Bob Admin",
            email="bob@example.invalid",
            now="2026-10-11 09:00:00",
        )

    # Code-review follow-up (LOW): an EMPTY `now` is refused by name, not
    # silently replaced with the wall clock — `if now` treats "" as absent.
    with pytest.raises(ValidationError, match=r"YYYY-MM-DDTHH:MM:SSZ"):
        create_registry(
            tmp_path / "empty",
            person="bob",
            name="Bob Admin",
            email="bob@example.invalid",
            now="",
        )


def test_canonical_json_typed_schema(tmp_path):
    """LLR-RH.1.3: canonical JSON = sorted keys, no whitespace,
    `ensure_ascii=False`, after NFC; the normative digest binds field names —
    the {"a":"ab","b":"c"} vs {"a":"a","b":"bc"} boundary pair hashes
    differently, and concatenation of values (M-CJ1's shape) is not the
    digest.  The typed schema's time format is exact (R18)."""
    canonical = canonical_json({"b": "café", "a": "é", "seq": 1})
    assert canonical == '{"a":"é","b":"café","seq":1}'
    assert " " not in canonical
    # NFC before hashing: the decomposed input digests as its composed form.
    decomposed = "café"
    assert nfc(decomposed) == "café"
    assert canonical_digest({"name": decomposed}) == canonical_digest({"name": "café"})
    # The field-boundary pair (R3): concatenation cannot distinguish these.
    assert canonical_digest({"a": "ab", "b": "c"}) != canonical_digest({"a": "a", "b": "bc"})
    concatenated = hashlib.sha256(b"abc").hexdigest()
    assert canonical_digest({"a": "ab", "b": "c"}) != concatenated
    # ensure_ascii=False: non-ASCII travels as itself.
    assert canonical_digest({"note": "é"}) == hashlib.sha256(
        '{"note":"é"}'.encode("utf-8")
    ).hexdigest()

    # The exact time format, through the public creation path.
    create_registry(
        tmp_path, person="ana", name="Ana", email="ana@example.invalid", now=NOW
    )
    with pytest.raises(ValidationError, match=r"YYYY-MM-DDTHH:MM:SSZ"):
        create_registry(
            tmp_path / "offset",
            person="ana",
            name="Ana",
            email="ana@example.invalid",
            now="2026-10-11T09:00:00+00:00",
        )
    with pytest.raises(ValidationError, match=r"YYYY-MM-DDTHH:MM:SSZ"):
        create_registry(
            tmp_path / "fraction",
            person="ana",
            name="Ana",
            email="ana@example.invalid",
            now="2026-10-11T09:00:00.000Z",
        )


def test_email_sha256_roundtrip(tmp_path):
    """LLR-RH.1.4: the email is stored ONLY as sha256 of the lowercased
    address (R12); a clear-text email scan over the written config finds 0
    matches (M-EH1's arm), and an identity matches by the same hash."""
    mixed = "BOB@Example.Invalid"
    assert email_sha256(mixed) == email_sha256("bob@example.invalid")
    assert email_sha256(mixed) == hashlib.sha256(b"bob@example.invalid").hexdigest()

    create_registry(tmp_path, person="bob", name="Bob Admin", email=mixed, now=NOW)
    written = (tmp_path / "reqharness" / "config.yml").read_bytes()
    assert CLEAR_EMAIL_RE.search(written) is None
    assert mixed.encode() not in written
    assert b"bob@example.invalid" not in written

    # Round-trip: the stored hash is what a reader of the SAME address
    # recomputes — the identity reader matches by hash, never in clear.
    config = load_config(tmp_path)
    (person,) = config.people
    assert person.email_sha256 == email_sha256(mixed)
    assert person.email_sha256 != email_sha256("other@example.invalid")
    assert person.name == "Bob Admin"  # display names stay in clear

    # Code-review follow-up (LOW): LLR-RH.1.4 says LOWERCASED and nothing
    # else — whitespace is NOT stripped (it is part of the address and
    # changes the hash), and the address is NFC-normalised before hashing.
    assert email_sha256(" bob@example.invalid") != email_sha256("bob@example.invalid")
    assert email_sha256("café@example.invalid") == email_sha256("cafe\u0301@example.invalid")


def test_time_format_is_ascii_fullmatch():
    """Code-review follow-up H1: the exact time format (R18) is a FULL match
    over ASCII digits only.  A trailing newline is refused (`$` would admit
    one) and Arabic-Indic digits are refused (a Unicode `\d` would admit
    them)."""
    assert check_time(NOW, where="chain", field="time") == NOW
    with pytest.raises(ValidationError, match=r"YYYY-MM-DDTHH:MM:SSZ"):
        check_time(NOW + "\n", where="chain", field="time")
    arabic_indic_2026 = "\u0662\u0660\u0662\u0666-10-11T09:00:00Z"
    with pytest.raises(ValidationError, match=r"YYYY-MM-DDTHH:MM:SSZ"):
        check_time(arabic_indic_2026, where="chain", field="time")


def test_create_registry_refuses_existing_registry(tmp_path):
    """Code-review follow-up H2: a registry is created only into empty
    ground.  When `config.yml` or `roles.yml` already exists the create is
    refused by name and the existing files are byte-identical afterwards —
    never overwritten, never partially written."""
    create_registry(
        tmp_path, person="bob", name="Bob Admin", email="bob@example.invalid", now=NOW
    )
    config_path = tmp_path / "reqharness" / "config.yml"
    roles_path = tmp_path / "reqharness" / "roles.yml"
    config_bytes = config_path.read_bytes()
    roles_bytes = roles_path.read_bytes()
    with pytest.raises(RegistryExistsError, match=r"already exists"):
        create_registry(
            tmp_path,
            person="eve",
            name="Eve Hostile",
            email="eve@example.invalid",
            now=NOW,
        )
    assert config_path.read_bytes() == config_bytes
    assert roles_path.read_bytes() == roles_bytes

    # A lone pre-existing file is refused too, named, and left untouched.
    lone = tmp_path / "lone" / "reqharness"
    lone.mkdir(parents=True)
    (lone / "config.yml").write_bytes(b"hand-written\n")
    with pytest.raises(RegistryExistsError, match=r"config\.yml"):
        create_registry(
            tmp_path / "lone",
            person="eve",
            name="Eve Hostile",
            email="eve@example.invalid",
            now=NOW,
        )
    assert (lone / "config.yml").read_bytes() == b"hand-written\n"
    assert not (lone / "roles.yml").exists()


def test_check_int_rejects_bool():
    """Code-review follow-up M1: `seq`/`roles_seq` are exactly `int` —
    `type(v) is int`, not isinstance, because `bool` subclasses `int` and
    `True` must never count as seq 1.  Str and float stand-ins are refused
    too."""
    assert check_int(1, where="roles.yml", field="seq") == 1
    for bad in (True, False, "1", 1.0, None):
        with pytest.raises(ValidationError, match=r"must be an int"):
            check_int(bad, where="roles.yml", field="seq")


def test_nfc_refuses_colliding_keys():
    """Code-review follow-up M3: two keys that collapse to the same NFC
    string are refused by name — otherwise a mapping silently loses one
    entry and two differently-spelled documents hash identically (R3)."""
    decomposed_vs_composed = {"cafe\u0301": 1, "caf\u00e9": 2}
    with pytest.raises(NfcKeyCollision, match=r"collide after NFC"):
        nfc(decomposed_vs_composed)
    with pytest.raises(NfcKeyCollision):
        canonical_digest(decomposed_vs_composed)
    # Distinct keys still normalise and keep their values.
    assert nfc({"caf\u00e9": 1, "tea": 2}) == {"caf\u00e9": 1, "tea": 2}


def _load_in_subprocess(tmp_path: Path, text: str) -> tuple[object, float]:
    """Run `load_documents` on *text* in a fresh interpreter (cwd = repo
    root, so `import mapper` resolves) and return (CompletedProcess, seconds).

    SEC F2 arms run in a SUBPROCESS on purpose: a C-stack overflow on
    Windows kills the whole process — out there it surfaces as a non-zero or
    negative exit code (or a timeout), never as a lost pytest run."""
    import subprocess
    import sys
    import time

    attack = tmp_path / "attack.yml"
    attack.write_text(text, encoding="utf-8")
    snippet = (
        "import sys;from pathlib import Path;"
        "from mapper.reqharness.config import load_documents;"
        "load_documents(Path(sys.argv[1]).read_text(encoding='utf-8'),"
        "where='reqharness/roles.yml');print('loaded')"
    )
    root = Path(__file__).resolve().parent.parent
    start = time.perf_counter()
    try:
        proc = subprocess.run(
            [sys.executable, "-B", "-c", snippet, str(attack)],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=root,
        )
    except subprocess.TimeoutExpired:
        raise AssertionError("the loader hung on a bounded input (superlinear parse)")
    return proc, time.perf_counter() - start


def test_nesting_event_stream_refuses_superlinear_depth():
    """SEC F2 (DDR follow-up, DDRFIX-C mechanism): the AUTHORITATIVE depth
    bound is the EVENT STREAM — `yaml.parse` counts collection start events
    and refuses depth > LIMIT_NESTING_DEPTH by name BEFORE compose/construct —
    so 64 KB of `[` flow nesting is refused as `nesting too deep` in well
    under a second (the parser's superlinear behaviour never runs), the same
    ceiling holds on block indentation, and a legitimate depth-10 document
    still loads."""
    import time

    attack = "[" * (64 * 1024)
    start = time.perf_counter()
    with pytest.raises(ValidationError) as excinfo:
        load_documents(attack, where="reqharness/reviews/attack.yml")
    # K3 re-check LOW-1: the named refusal surfaces as itself — one
    # `<where>:` prefix, never re-wrapped as `malformed YAML (...)`.
    assert str(excinfo.value) == (
        "reqharness/reviews/attack.yml: nesting too deep (depth 65 > 64)"
    )
    assert "malformed YAML" not in str(excinfo.value)
    elapsed = time.perf_counter() - start
    assert elapsed < 2.0, f"the event-stream check was not cheap: {elapsed:.2f}s"

    # the same ceiling on block indentation, by name — exact message again
    deep_block = "".join(f"{'  ' * i}k{i}:\n" for i in range(LIMIT_NESTING_DEPTH + 6))
    with pytest.raises(ValidationError) as excinfo:
        load_documents(deep_block, where="reqharness/reviews/deep.yml")
    assert str(excinfo.value) == (
        "reqharness/reviews/deep.yml: nesting too deep (depth 65 > 64)"
    )

    # a legitimate depth-10 document still loads
    legit = "".join(f"{'  ' * i}k{i}:\n" for i in range(10)) + "  " * 10 + "leaf: 1\n"
    documents = load_documents(legit, where="reqharness/config.yml")
    cursor = documents[0]
    for i in range(10):
        cursor = cursor[f"k{i}"]
    assert cursor == {"leaf": 1}


def test_nesting_event_stream_refuses_lexically_bypassed_shapes(tmp_path):
    """SEC F2 re-verification (DDRFIX-C): every shape the OLD lexical
    pre-scan miscounted is refused by the event-stream check — the
    apostrophe 'open quote' bypass (`n: it's` / `x#'` / `say "hi` swallowing
    the rest of the file), compact block sequences (`- - - …`), complex keys
    (`? ? ? …`), a genuinely deep block nest behind an apostrophe line, a
    mixed flow/block tree, and the multi-MB flow flood.  Each arm runs in a
    SUBPROCESS: the refusal names `nesting too deep`, exits non-zero, and
    lands in < 2 s (the pre-fix code crashed the interpreter's C stack on
    the deep arms — a crash out there is a negative exit code, a RED here).
    """
    limit = LIMIT_NESTING_DEPTH
    block_1024 = (
        "".join(f"{'  ' * i}k{i}:\n" for i in range(1024)) + "  " * 1024 + "leaf: 1\n"
    )
    mixed_200 = (
        "".join(f"{'  ' * i}k{i}:\n" for i in range(199)) + "  " * 199 + "- [a, b]\n"
    )
    arms = {
        "apostrophe + 64KB flow flood": "n: it's\nv: " + "[" * (64 * 1024),
        "hash-quote + 64KB flow flood": "x#':\n  v: " + "[" * (64 * 1024),
        "open double quote + flood": 'say "hi:\n  v: ' + "[" * (64 * 1024),
        "compact sequence 1000 deep": "-" + " - " * 999 + "x\n",
        "complex keys 1000 deep": "?" + " ? " * 999 + "x\n",
        "apostrophe + 1024 block nest": "n: it's\n" + block_1024,
        "mixed flow/block 200 deep": mixed_200,
        "4MB flow flood (roles.yml)": "v: " + "[" * (4 * 1024 * 1024) + "\n",
    }
    for label, text in arms.items():
        proc, elapsed = _load_in_subprocess(tmp_path, text)
        assert proc.returncode != 0, f"{label}: attack parsed clean ({proc.stdout!r})"
        assert "nesting too deep" in proc.stderr, f"{label}: {proc.stderr[-400:]}"
        assert elapsed < 2.0, f"{label}: refusal was not cheap: {elapsed:.2f}s"


def test_nesting_event_stream_boundary_and_quoted_scalars():
    """SEC F2 positives (DDRFIX-C): the boundary is exact — a depth-64
    document loads, depth 65 is refused by name — and 63 KB of brackets
    inside a PROPERLY QUOTED scalar is content, not nesting: it loads."""
    limit = LIMIT_NESTING_DEPTH
    at_limit = "[" * limit + '"x"' + "]" * limit
    (document,) = load_documents(at_limit, where="reqharness/roles.yml")
    cursor = document
    for _ in range(limit):
        (cursor,) = cursor
    assert cursor == "x"

    over_limit = "[" * (limit + 1) + '"x"' + "]" * (limit + 1)
    with pytest.raises(ValidationError) as excinfo:
        load_documents(over_limit, where="reqharness/roles.yml")
    # K3 re-check LOW-1: exactly one `<where>:` prefix on the named refusal
    assert str(excinfo.value) == "reqharness/roles.yml: nesting too deep (depth 65 > 64)"

    quoted = "v: '" + "[" * (63 * 1024) + "'\n"
    (document,) = load_documents(quoted, where="reqharness/roles.yml")
    assert document["v"] == "[" * (63 * 1024)
