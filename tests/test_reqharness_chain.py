"""HLR-RH.2 / HLR-RH.3 — the approved role chain: append rules, policy
binding, head binding, effective roles at a bound head, tamper/fork detection
and the `resolve` recovery.

The seventeen node names are the executed verification named in
`.dev-flow/2026-10-11-reqharness-batch/01-requirements.md` §3 for HLR-RH.2 and
HLR-RH.3 (including the R27 arms and LLR-RH.3.4's M-FR4 arm), plus the
code-review follow-up nodes (RHFIX23 F1–F3).  Every refusal
is asserted BY NAME (R9); the status words are asserted byte-for-byte
(LLR-RH.3.3 / AT-079).
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest
import yaml

from mapper.reqharness.canonical import chain_hash
from mapper.reqharness.chain import (
    append_policy,
    append_resolve,
    approve_pending,
    effective_roles,
    propose,
    read_event_file,
    reject_pending,
    verify_chain,
)
from mapper.reqharness.config import (
    GENESIS_PREV,
    LIMIT_EVENT_FILE_BYTES,
    LIMIT_ROLES_YML_BYTES,
    config_digest,
    create_registry,
    email_sha256,
    load_config,
    load_documents,
)
from mapper.reqharness.records import ValidationError

T0 = "2026-10-11T09:00:00Z"
T1 = "2026-10-11T09:01:00Z"
T2 = "2026-10-11T09:02:00Z"
T3 = "2026-10-11T09:03:00Z"
T4 = "2026-10-11T09:04:00Z"
T5 = "2026-10-11T09:05:00Z"
T6 = "2026-10-11T09:06:00Z"
T7 = "2026-10-11T09:07:00Z"

ROLES = Path("reqharness") / "roles.yml"
PENDING_NAME_RE = re.compile(r"\d{8}-[0-9a-f]{8}\.yml")


def _seed(root: Path) -> None:
    create_registry(
        root, person="bob", name="Bob Admin", email="bob@example.invalid", now=T0
    )


def _config_doc(root: Path):
    path = root / "reqharness" / "config.yml"
    (document,) = load_documents(
        path.read_text(encoding="utf-8"), where="reqharness/config.yml"
    )
    return path, document


def _add_ana(root: Path) -> None:
    """Add ana to the config, then re-bind it through an admin `policy`
    event (the edited config is otherwise `config changed without
    approval`)."""
    path, document = _config_doc(root)
    document["people"].append(
        {
            "id": "ana",
            "name": "Ana Reviewer",
            "email_sha256": email_sha256("ana@example.invalid"),
        }
    )
    path.write_text(
        yaml.safe_dump(document, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
        newline="\n",
    )
    append_policy(root, approved_by="bob", note="add ana", now=T1)


def _read_docs(root: Path) -> list[dict]:
    return load_documents(
        (root / ROLES).read_text(encoding="utf-8"), where="reqharness/roles.yml"
    )


def _write_docs(root: Path, docs: list[dict]) -> None:
    text = "".join(
        "---\n" + yaml.safe_dump(d, sort_keys=False, allow_unicode=True) for d in docs
    )
    (root / ROLES).write_text(text, encoding="utf-8", newline="\n")


def _append_raw(root: Path, event: dict) -> None:
    with (root / ROLES).open("a", encoding="utf-8", newline="\n") as handle:
        handle.write("---\n" + yaml.safe_dump(event, sort_keys=False, allow_unicode=True))


def _event(
    prev: str,
    seq: int,
    *,
    time: str,
    action: str,
    requested_by: str,
    approved_by: str,
    person: str,
    role: str,
    note: str = "",
    resolve_excludes: str | None = None,
) -> dict:
    """A hand-built chain event (used for forks/tampers — never the write
    path), wired like the writer: roles_seq = seq - 1, roles_hash = prev."""
    body: dict = {
        "seq": seq,
        "time": time,
        "requested_by": requested_by,
        "approved_by": approved_by,
        "action": action,
        "person": person,
        "role": role,
        "note": note,
        "roles_seq": 1 if action == "genesis" else seq - 1,
        "roles_hash": GENESIS_PREV if action == "genesis" else prev,
        "prev_hash": prev,
    }
    if resolve_excludes is not None:
        body["resolve_excludes"] = resolve_excludes
    body["this_hash"] = chain_hash(prev, body)
    return body


def _fix_links(docs: list[dict], *, normalize: bool = True) -> list[dict]:
    """Recompute the chain links (and, unless *normalize* is False, the head
    bindings) — the consistent-rewrite fixture builder."""
    prev = GENESIS_PREV
    for doc in docs:
        doc["prev_hash"] = prev
        if normalize:
            doc["roles_seq"] = 1 if doc["action"] == "genesis" else doc["seq"] - 1
            doc["roles_hash"] = prev
        doc["this_hash"] = chain_hash(
            prev, {k: v for k, v in doc.items() if k != "this_hash"}
        )
        prev = doc["this_hash"]
    return docs


def _fork_parts(root: Path, *, bad_child: bool = False):
    """genesis + policy, then TWO children claiming the policy head (the
    parallel-PR merge shape).  With *bad_child*, child B is self-approved
    (fails the approval rule at its own bound head — M-FR4's shape)."""
    _seed(root)
    _add_ana(root)
    base = _read_docs(root)
    head = verify_chain(root).events[-1].this_hash
    child_a = _event(
        head, 3, time=T2, action="grant",
        requested_by="bob", approved_by="bob",
        person="ana", role="req-reviewer", note="branch A",
    )
    child_b = _event(
        head, 3, time=T2, action="grant",
        requested_by="bob",
        approved_by="bob" if bad_child else "bob",
        person="bob" if bad_child else "ana",
        role="req-reviewer" if bad_child else "admin",
        note="self-approved branch B" if bad_child else "branch B",
    )
    return base, child_a, child_b


def test_admin_applies_to_someone_else_in_one_event(tmp_path):
    """LLR-RH.2.1: an admin's grant about another person is ONE event with
    `requested_by == approved_by == that admin`, bound to the current head;
    verify stays clean and the grant is in force (M-CH1 forces a two-event
    path)."""
    _seed(tmp_path)
    _add_ana(tmp_path)
    result = propose(
        tmp_path, requester="bob", action="grant",
        person="ana", role="req-reviewer", now=T2,
    )
    assert result is None  # applied, not pended
    docs = _read_docs(tmp_path)
    assert len(docs) == 3  # genesis, policy, grant — exactly ONE new event
    grant = docs[-1]
    assert grant["requested_by"] == grant["approved_by"] == "bob"
    report = verify_chain(tmp_path)
    assert report.ok
    previous_head = report.events[1].this_hash  # the policy event's hash
    assert grant["roles_hash"] == previous_head  # R2: records the head made against
    assert grant["prev_hash"] == previous_head
    assert effective_roles(report)["ana"] == ("req-reviewer",)


def test_self_change_and_non_admin_stay_pending(tmp_path):
    """LLR-RH.2.2: a change about the requester themselves, or by a
    non-admin, writes ONE pending file under `reqharness/pending/` and 0 bytes
    to roles.yml; a pending self-change becomes appendable once a second
    admin approves it (M-CH2 allows self-approval)."""
    _seed(tmp_path)
    _add_ana(tmp_path)
    roles_bytes = (tmp_path / ROLES).read_bytes()

    pending_self = propose(
        tmp_path, requester="bob", action="grant",
        person="bob", role="req-reviewer", now=T2,
    )
    assert pending_self is not None and pending_self.is_file()
    assert pending_self.parent == tmp_path / "reqharness" / "pending"
    assert PENDING_NAME_RE.fullmatch(pending_self.name)
    assert (tmp_path / ROLES).read_bytes() == roles_bytes  # nothing appended

    pending_ana = propose(
        tmp_path, requester="ana", action="grant",
        person="ana", role="admin", now=T2,
    )
    assert pending_ana is not None and pending_ana != pending_self
    assert PENDING_NAME_RE.fullmatch(pending_ana.name)
    assert (tmp_path / ROLES).read_bytes() == roles_bytes
    pending_dir = tmp_path / "reqharness" / "pending"
    assert len(list(pending_dir.iterdir())) == 2  # exactly 1 file per request

    # approvals: a non-admin cannot, and nobody approves their own request
    with pytest.raises(ValidationError, match="no admin"):
        approve_pending(tmp_path, pending=pending_self.name, approver="ana", now=T2)
    with pytest.raises(ValidationError, match="their own"):
        approve_pending(tmp_path, pending=pending_self.name, approver="bob", now=T2)

    # a second admin exists: bob grants ana admin in one key (T3)...
    assert propose(
        tmp_path, requester="bob", action="grant",
        person="ana", role="admin", now=T3,
    ) is None
    # ...and the held self-change is appended under ana's approval
    event = approve_pending(
        tmp_path, pending=pending_self.name, approver="ana", now=T4
    )
    assert event.requested_by == "bob" and event.approved_by == "ana"
    report = verify_chain(tmp_path)
    assert report.ok
    assert effective_roles(report)["bob"] == ("admin", "req-reviewer")
    assert effective_roles(report)["ana"] == ("admin",)


def test_genesis_only_at_position_one(tmp_path):
    """RHFIX F1: `genesis` is valid ONLY at walk position 1 — the pin is the
    exact identity `(event.action == "genesis") == (position == 1)` in
    `_check_event`, and the `_passes_approval` genesis shortcut holds only
    with no prefix.  A seq-2 `genesis` by a non-admin (its links and head
    binding fully valid) must break the chain at its document, never mint
    an admin (the reviewer reproduced: effective_roles -> eve admin).

    Mutant M-CH6 (remove the position pin and restore the unconditional
    genesis shortcut) -> the forged genesis verifies clean, eve becomes
    admin -> this node is RED."""
    _seed(tmp_path)
    docs = _read_docs(tmp_path)
    genesis_hash = docs[0]["this_hash"]
    forged = _event(
        genesis_hash, 2, time=T1, action="genesis",
        requested_by="eve", approved_by="eve",
        person="eve", role="admin", note="forged second genesis",
    )
    forged["roles_hash"] = genesis_hash  # bind the real head, so the
    forged["config_hash"] = config_digest(load_config(tmp_path))  # F3-required
    body = {k: v for k, v in forged.items() if k != "this_hash"}
    forged["this_hash"] = chain_hash(genesis_hash, body)  # position pin fails
    _append_raw(tmp_path, forged)
    report = verify_chain(tmp_path)
    assert report.status == "config changed without approval"  # exact word
    assert report.broken_index == 1  # the forged document, at its walk position
    assert effective_roles(report) == {"bob": ("admin",)}  # no extra admin

    # the mirror arm: a non-genesis action can never occupy position 1
    mirror = tmp_path / "mirror"
    _seed(mirror)
    impostor = _event(
        GENESIS_PREV, 1, time=T0, action="grant",
        requested_by="bob", approved_by="bob",
        person="ana", role="admin", note="not a genesis",
    )
    impostor["roles_seq"] = 1  # the declared-root binding of a position-1 event
    body = {k: v for k, v in impostor.items() if k != "this_hash"}
    impostor["this_hash"] = chain_hash(GENESIS_PREV, body)
    _write_docs(mirror, [impostor])
    report = verify_chain(mirror)
    assert report.status == "config changed without approval"
    assert report.broken_index == 0
    assert report.events == ()  # nothing verified: no genesis, no admin


def test_effective_roles_at_time_t(tmp_path):
    """LLR-RH.2.3 (as amended by LED-2026-10-11-reqharness-batch.31): roles
    in force AT A BOUND HEAD fold only verified-prefix events whose OWN
    `seq` is <= the bound seq — a grant never retro-authorizes an earlier
    head, and the boundary instant (bound seq == the grant event's own
    `seq`) is INCLUSIVE (M-CH5 flips the `<=` to `<`).  Folding on
    `roles_seq` would leak an event at seq k+1 (roles_seq k) into head k."""
    _seed(tmp_path)
    _add_ana(tmp_path)
    assert propose(
        tmp_path, requester="bob", action="grant",
        person="ana", role="req-reviewer", now=T2,
    ) is None
    report = verify_chain(tmp_path)
    hashes = [e.this_hash for e in report.events]
    assert report.events[2].action == "grant"
    assert report.events[2].seq == 3
    assert report.events[2].roles_seq == 2  # binds head 2

    # pre-grant heads exclude the grant — at head 2 the grant (seq 3,
    # roles_seq 2) is NOT in force: a `roles_seq` fold would leak it (F2)
    assert effective_roles(report, 1, hashes[0]) == {"bob": ("admin",)}
    assert effective_roles(report, 2, hashes[1]) == {"bob": ("admin",)}
    # boundary: bound seq == the grant event's own seq -> included
    assert effective_roles(report, 3, hashes[2]) == {
        "bob": ("admin",),
        "ana": ("req-reviewer",),
    }

    # a later revoke never retro-reaches an earlier head either
    assert propose(
        tmp_path, requester="bob", action="revoke",
        person="ana", role="req-reviewer", now=T3,
    ) is None
    report = verify_chain(tmp_path)
    hashes = [e.this_hash for e in report.events]
    assert effective_roles(report, 3, hashes[2])["ana"] == ("req-reviewer",)
    assert "ana" not in effective_roles(report, 4, hashes[3])

    # a grant at seq 2 is NOT in force at head 1 (the F2 ruling fixture):
    # the event binds head 1 exactly (roles_seq 1, roles_hash = genesis)
    leap = tmp_path / "leap"
    _seed(leap)
    docs = _read_docs(leap)
    genesis_hash = docs[0]["this_hash"]
    early = _event(
        genesis_hash, 2, time=T1, action="grant",
        requested_by="bob", approved_by="bob",
        person="ana", role="req-reviewer", note="grant at seq 2",
    )
    _append_raw(leap, early)
    report = verify_chain(leap)
    assert report.ok
    assert effective_roles(report, 1, genesis_hash) == {"bob": ("admin",)}
    assert effective_roles(report, 2, report.events[1].this_hash) == {
        "bob": ("admin",),
        "ana": ("req-reviewer",),
    }

    # a bound head that does not exist in the chain is not verifiable
    with pytest.raises(ValidationError, match="not in the verified chain"):
        effective_roles(report, 99, "ab" * 32)
    with pytest.raises(ValidationError, match="not in the verified chain"):
        effective_roles(report, 2, genesis_hash)  # right seq, wrong hash


def test_policy_event_binds_config(tmp_path):
    """LLR-RH.2.4: the live config's canonical hash must equal the newest
    verified policy-bearing event's `config_hash`; a hand-edited config is
    `config changed without approval` with the last approved policy in force
    and appends frozen, until an admin re-binds it (M-P1 skips the check)."""
    _seed(tmp_path)
    report = verify_chain(tmp_path)
    assert report.ok
    assert report.status == "chain verified"
    original = config_digest(load_config(tmp_path))
    assert report.policy_config_hash == original  # genesis binds it (R15)

    path, document = _config_doc(tmp_path)
    document["people"].append(
        {
            "id": "ana",
            "name": "Ana Reviewer",
            "email_sha256": email_sha256("ana@example.invalid"),
        }
    )
    path.write_text(
        yaml.safe_dump(document, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
        newline="\n",
    )
    edited = config_digest(load_config(tmp_path))
    assert edited != original

    report = verify_chain(tmp_path)
    assert not report.ok
    assert report.status == "config changed without approval"
    assert report.policy_config_hash == original  # last approved policy in force

    # read-only tamper state: role appends are frozen
    with pytest.raises(ValidationError, match="not appendable"):
        propose(
            tmp_path, requester="bob", action="grant",
            person="bob", role="req-reviewer", now=T2,
        )

    # an admin re-binds the edited config in ONE policy event
    event = append_policy(tmp_path, approved_by="bob", note="bind edited config", now=T1)
    assert event.action == "policy"
    report = verify_chain(tmp_path)
    assert report.ok
    assert report.policy_config_hash == edited == config_digest(load_config(tmp_path))

    # only an admin binds policy
    with pytest.raises(ValidationError, match="no admin"):
        append_policy(tmp_path, approved_by="ana", now=T2)


def test_policy_event_requires_config_hash(tmp_path):
    """RHFIX F3 (R15/LLR-RH.2.4): `config_hash` is REQUIRED on `genesis`
    and `policy` events — a policy-bearing event must bind a config hash,
    never nothing.  A document without it is refused at the typed schema,
    named by file AND document (R9), so the chain can never verify under a
    policy that binds nothing and every append stays refused.

    Mutant F3a (drop the requirement) -> both fixtures pass silently ->
    this node is RED."""
    _seed(tmp_path)
    _add_ana(tmp_path)  # genesis + policy, both carrying config_hash
    docs = _read_docs(tmp_path)
    del docs[0]["config_hash"]  # the genesis event
    _fix_links(docs, normalize=False)  # links hold; the schema does not
    _write_docs(tmp_path, docs)
    with pytest.raises(
        ValidationError, match=r"roles\.yml: document 1: missing key\(s\): config_hash"
    ):
        verify_chain(tmp_path)

    docs[0]["config_hash"] = config_digest(load_config(tmp_path))
    del docs[1]["config_hash"]  # the policy event
    _fix_links(docs, normalize=False)
    _write_docs(tmp_path, docs)
    with pytest.raises(
        ValidationError, match=r"roles\.yml: document 2: missing key\(s\): config_hash"
    ):
        verify_chain(tmp_path)


def test_head_binding_unknown_head_not_verifiable(tmp_path):
    """LLR-RH.2.5 / LLR-RH.4.5: an event bound to a head that
    does not exist in the chain fails verify (M-HB1 accepts
    unknown bound heads); a truncated tail and a genesis
    rewrite fail at the offending document; `time` must be
    non-decreasing even under a consistent rewrite.
    (LLR-RH.4.5's executed verification names this
    node for the unknown-head arm.)"""
    # an event with valid links but a bogus recorded head
    _seed(tmp_path)
    _add_ana(tmp_path)
    assert propose(
        tmp_path, requester="bob", action="grant",
        person="ana", role="req-reviewer", now=T2,
    ) is None
    docs = _read_docs(tmp_path)
    docs[-1]["roles_hash"] = "ab" * 32
    _fix_links(docs, normalize=False)  # links hold; the binding does not
    _write_docs(tmp_path, docs)
    report = verify_chain(tmp_path)
    assert not report.ok
    assert report.status == "config changed without approval"
    assert report.broken_index == 2

    # tail truncation: the survivor claims a head the file no longer contains
    trunc = tmp_path / "trunc"
    _seed(trunc)
    _add_ana(trunc)
    assert propose(
        trunc, requester="bob", action="grant",
        person="ana", role="req-reviewer", now=T2,
    ) is None
    docs = _read_docs(trunc)
    del docs[1]  # the policy event: the grant now claims a head the file lacks
    _write_docs(trunc, docs)
    report = verify_chain(trunc)
    assert not report.ok
    assert report.broken_index == 1  # the survivor — the doc the walk cannot reach

    # genesis rewrite (naive hand edit, hashes stale)
    gen = tmp_path / "gen"
    _seed(gen)
    docs = _read_docs(gen)
    docs[0]["person"] = "mallory"
    _write_docs(gen, docs)
    report = verify_chain(gen)
    assert not report.ok
    assert report.broken_index == 0

    # decreasing time, recomputed consistently — still not verifiable
    dec = tmp_path / "dec"
    _seed(dec)
    _add_ana(dec)
    docs = _read_docs(dec)
    docs[1]["time"] = "2026-10-11T08:59:59Z"  # the policy event moves before genesis
    _fix_links(docs)
    _write_docs(dec, docs)
    report = verify_chain(dec)
    assert not report.ok
    assert report.status == "config changed without approval"
    assert report.broken_index == 1


def test_hand_edit_breaks_chain_and_keeps_last_verified(tmp_path):
    """LLR-RH.3.1/3.3: a hand edit anywhere in roles.yml breaks the chain at
    the spliced document; the status word is exactly `config changed without
    approval`; effective roles equal the last VERIFIED prefix (M-CH3 skips
    the per-document hash recompute).  The osopen confinement refuses a
    junction on the way to roles.yml, named."""
    _seed(tmp_path)
    _add_ana(tmp_path)
    assert propose(
        tmp_path, requester="bob", action="grant",
        person="ana", role="req-reviewer", now=T2,
    ) is None
    docs = _read_docs(tmp_path)
    docs[2]["role"] = "admin"  # the hand edit: ana's grant becomes admin
    _write_docs(tmp_path, docs)  # hashes now stale
    report = verify_chain(tmp_path)
    assert not report.ok
    assert report.status == "config changed without approval"  # exact word
    assert report.broken_index == 2  # the spliced document, at its walk position
    assert effective_roles(report) == {"bob": ("admin",)}  # last verified prefix only

    # confinement: a junction on the path to roles.yml is refused, named
    linked = tmp_path / "linked"
    linked.mkdir()
    try:
        subprocess.run(
            ["cmd", "/c", "mklink", "/J",
             str(linked / "reqharness"), str(tmp_path / "reqharness")],
            check=True, capture_output=True,
        )
    except (OSError, subprocess.CalledProcessError):
        pytest.skip("junction creation is unavailable on this host")
    with pytest.raises(ValidationError, match=r"reqharness/roles\.yml: refused \(link\)"):
        verify_chain(linked)


def test_merge_fork_is_detected(tmp_path):
    """LLR-RH.3.2: two documents claiming the same `prev_hash` exclude BOTH
    children from authority — deterministically on every clone regardless of
    document order — reported `chain forked at seq N` (M-CH4 dedupes the fork
    by seq; M-FR2 keeps a child in authority)."""
    base, child_a, child_b = _fork_parts(tmp_path)
    child_hashes = sorted([child_a["this_hash"], child_b["this_hash"]])
    verdicts = []
    for first, second in ((child_a, child_b), (child_b, child_a)):
        _write_docs(tmp_path, [*base, first, second])
        report = verify_chain(tmp_path)
        assert report.status == "chain forked at seq 3"
        assert report.fork_seq == 3
        assert len(report.events) == 2  # the prefix stops at the fork
        assert report.excluded == tuple(child_hashes)
        assert effective_roles(report) == {"bob": ("admin",)}  # pre-fork roles
        verdicts.append((report.status, report.events, report.excluded))
    assert verdicts[0] == verdicts[1]  # 2/2 document orders agree


def test_fork_resolve_event_recovers(tmp_path):
    """LLR-RH.3.4: the only legal continuation after a fork is an
    admin-approved `resolve` event — `prev_hash` = the CHOSEN child,
    `resolve_excludes` = the excluded sibling — after which the chain
    verifies again and authority returns (R16; M-FR1 resolves by keeping the
    wrong child or naming the wrong sibling)."""
    base, child_a, child_b = _fork_parts(tmp_path)
    _write_docs(tmp_path, [*base, child_a, child_b])
    assert verify_chain(tmp_path).status == "chain forked at seq 3"

    resolve = append_resolve(
        tmp_path, approved_by="bob",
        chosen_hash=child_a["this_hash"], excludes_hash=child_b["this_hash"],
        note="keep branch A", now=T3,
    )
    assert resolve.action == "resolve"
    assert resolve.prev_hash == child_a["this_hash"]
    assert resolve.resolve_excludes == child_b["this_hash"]

    report = verify_chain(tmp_path)
    assert report.ok  # the chain verifies again
    assert len(report.events) == 4  # exactly the resolve beyond the fork point
    assert report.excluded == (child_b["this_hash"],)
    assert effective_roles(report)["ana"] == ("req-reviewer",)  # the chosen grant
    assert effective_roles(report)["ana"] != ("admin",)  # the excluded one is not


def test_fork_recovery_reappend_on_head(tmp_path):
    """HLR-RH.2 (recovery arm): the documented MANUAL procedure of the
    chain.py module docstring — the operator hand-appends ONE `resolve`
    document on the chosen head — recovers the fork; verify is clean and the
    excluded sibling stays excluded."""
    base, child_a, child_b = _fork_parts(tmp_path)
    _write_docs(tmp_path, [*base, child_a, child_b])
    manual = _event(
        child_a["this_hash"], 4, time=T3, action="resolve",
        requested_by="bob", approved_by="bob", person="", role="",
        note="manual procedure", resolve_excludes=child_b["this_hash"],
    )
    _append_raw(tmp_path, manual)  # one document appended on the chosen head
    report = verify_chain(tmp_path)
    assert report.ok
    assert len(report.events) == 4
    assert report.excluded == (child_b["this_hash"],)
    assert effective_roles(report)["ana"] == ("req-reviewer",)


def test_verify_walks_by_prev_hash_in_order_fork_resolve(tmp_path):
    """R27 (LLR-RH.3.1/3.2/3.4): the walk is BY `prev_hash`, NOT by file
    position — the in-order parent -> childA -> childB -> resolve stream
    verifies: childB claims an already-claimed parent (a fork sibling, kept
    excluded) and the resolve's `prev_hash` (the chosen child) legitimately
    continues the walk (M-FR3 walks by file position and mis-walks)."""
    base, child_a, child_b = _fork_parts(tmp_path)
    resolve = _event(
        child_a["this_hash"], 4, time=T3, action="resolve",
        requested_by="bob", approved_by="bob", person="", role="",
        note="keep branch A", resolve_excludes=child_b["this_hash"],
    )
    _write_docs(tmp_path, [base[0], base[1], child_a, child_b, resolve])
    report = verify_chain(tmp_path)
    assert report.ok
    assert [e.action for e in report.events] == ["genesis", "policy", "grant", "resolve"]
    assert report.excluded == (child_b["this_hash"],)


def test_resolve_naming_non_sibling_is_invalid(tmp_path):
    """R27 (LLR-RH.3.4): a `resolve` whose `resolve_excludes` names a hash
    that is NOT one of the fork's children fails verify — a resolve cannot
    mint exclusions out of thin air (M-FR1's wrong-sibling arm)."""
    base, child_a, child_b = _fork_parts(tmp_path)
    bogus = _event(
        child_a["this_hash"], 4, time=T3, action="resolve",
        requested_by="bob", approved_by="bob", person="", role="",
        note="name a stranger", resolve_excludes="ab" * 32,
    )
    _write_docs(tmp_path, [*base, child_a, child_b, bogus])
    report = verify_chain(tmp_path)
    assert not report.ok
    assert report.status == "chain broken"


def test_multi_event_excluded_branch_is_broken(tmp_path):
    """R27 (LLR-RH.3.1/3.2): a fork whose excluded branch has DESCENDANTS
    (parent -> {childA, childB}, childB -> grandchild) is `chain broken` —
    single-event forks only this batch; multi-event branch recovery is
    deferred (B-126)."""
    base, child_a, child_b = _fork_parts(tmp_path)
    grandchild = _event(
        child_b["this_hash"], 4, time=T3, action="grant",
        requested_by="bob", approved_by="bob",
        person="ana", role="admin", note="descendant of the excluded branch",
    )
    _write_docs(tmp_path, [*base, child_a, child_b, grandchild])
    report = verify_chain(tmp_path)
    assert not report.ok
    assert report.status == "chain broken"
    assert report.broken_index == 4  # the descendant, at its walk position


def test_resolve_chosen_child_must_pass_approval_rule(tmp_path):
    """R27 (LLR-RH.3.4): a `resolve` is valid only when the chosen child
    itself passes the approval rule at its own bound head — a
    never-approvable (self-approved) child cannot be legitimized by resolve
    (M-FR4 skips the chosen child's approval check)."""
    base, child_a, child_b = _fork_parts(tmp_path, bad_child=True)
    _write_docs(tmp_path, [*base, child_a, child_b])
    # the API refuses to legitimize the self-approved child
    with pytest.raises(ValidationError, match="approval rule"):
        append_resolve(
            tmp_path, approved_by="bob",
            chosen_hash=child_b["this_hash"], excludes_hash=child_a["this_hash"],
            now=T3,
        )
    # a hand-written resolve choosing it fails verify as well
    resolve = _event(
        child_b["this_hash"], 4, time=T3, action="resolve",
        requested_by="bob", approved_by="bob", person="", role="",
        note="legitimize the self-approved child", resolve_excludes=child_a["this_hash"],
    )
    _append_raw(tmp_path, resolve)
    report = verify_chain(tmp_path)
    assert not report.ok
    assert report.excluded == tuple(sorted([child_a["this_hash"], child_b["this_hash"]]))


def test_input_limits_reported_by_name(tmp_path, monkeypatch):
    """LLR-RH.3.5 (R9/R26): the 5 refusal fixtures — oversize roles.yml,
    oversize review file, anchors/aliases, duplicate keys, deep nesting —
    plus a syntax-malformed YAML document in EACH of the four file kinds
    (config, roles.yml, review, pending): every refusal names the file, never
    a traceback, never silently skipped (M-LM1 skips the size check)."""
    _seed(tmp_path)

    # 1. oversize roles.yml (4 MB + 1)
    path = tmp_path / ROLES
    text = path.read_text(encoding="utf-8")
    path.write_text(
        text + "#" * (LIMIT_ROLES_YML_BYTES + 1), encoding="utf-8", newline="\n"
    )
    with pytest.raises(ValidationError, match=r"roles\.yml: file too large"):
        verify_chain(tmp_path)

    # 2. oversize review file (64 KB + 1)
    reviews = tmp_path / "reqharness" / "reviews"
    reviews.mkdir(parents=True)
    (reviews / "big.yml").write_bytes(b"note: " + b"x" * LIMIT_EVENT_FILE_BYTES)
    with pytest.raises(ValidationError, match=r"reviews/big\.yml: file too large"):
        read_event_file(tmp_path, "reviews/big.yml")

    # 3. anchors/aliases in roles.yml
    path.write_text("base: &b 1\nnote: *b\n", encoding="utf-8", newline="\n")
    with pytest.raises(ValidationError, match=r"roles\.yml: .*anchors and aliases"):
        verify_chain(tmp_path)

    # 4. duplicate keys in a pending file
    pending = tmp_path / "reqharness" / "pending"
    pending.mkdir(parents=True)
    (pending / "dup.yml").write_text(
        "requested_by: ana\nrequested_by: bob\n", encoding="utf-8", newline="\n"
    )
    with pytest.raises(ValidationError, match=r"pending/dup\.yml: .*duplicate key"):
        load_documents(
            read_event_file(tmp_path, "pending/dup.yml"),
            where="reqharness/pending/dup.yml",
        )

    # 5. deep nesting — the SEC F2 linear pre-scan refuses flow
    # depth and block-indent depth > 64 by name BEFORE the parser (the
    # old RecursionError/ValueError ladder stays as the backstop below);
    # K3 re-check LOW-1: the named refusal surfaces as itself — exactly one
    # `<where>:` prefix, never re-wrapped as `malformed YAML (...)`
    (reviews / "deep.yml").write_text("[[" * 300 + "1" + "]]" * 300, encoding="utf-8")
    with pytest.raises(ValidationError) as excinfo:
        load_documents(
            read_event_file(tmp_path, "reviews/deep.yml"),
            where="reqharness/reviews/deep.yml",
        )
    assert str(excinfo.value) == "reqharness/reviews/deep.yml: nesting too deep (depth 65 > 64)"
    deep_block = "".join(f"{'  ' * i}k{i}:\n" for i in range(70))
    (reviews / "deepblock.yml").write_text(deep_block, encoding="utf-8", newline="\n")
    with pytest.raises(ValidationError) as excinfo:
        load_documents(
            read_event_file(tmp_path, "reviews/deepblock.yml"),
            where="reqharness/reviews/deepblock.yml",
        )
    assert str(excinfo.value) == (
        "reqharness/reviews/deepblock.yml: nesting too deep (depth 65 > 64)"
    )
    # ... and the bare ValueError shape (a >4300-digit scalar, the
    # mapper/store.py:706-720 precedent) through the C loader
    # itself still degrades to the named error
    (reviews / "huge.yml").write_text(
        "note: " + "9" * 5000 + "\n", encoding="utf-8", newline="\n"
    )
    with pytest.raises(ValidationError, match=r"reviews/huge\.yml: malformed YAML"):
        load_documents(
            read_event_file(tmp_path, "reviews/huge.yml"),
            where="reqharness/reviews/huge.yml",
        )

    # syntax-malformed YAML in EACH of the four file kinds — 4/4 named (R26)
    (tmp_path / "reqharness" / "config.yml").write_text(
        'version: "1"\npeople: [unclosed\n', encoding="utf-8", newline="\n"
    )
    with pytest.raises(ValidationError, match=r"config\.yml: malformed YAML"):
        load_config(tmp_path)

    path.write_text("seq: 1\nnote: [unclosed\n", encoding="utf-8", newline="\n")
    with pytest.raises(ValidationError, match=r"roles\.yml: malformed YAML"):
        verify_chain(tmp_path)

    (reviews / "bad.yml").write_text("verdict: [unclosed\n", encoding="utf-8", newline="\n")
    with pytest.raises(ValidationError, match=r"reviews/bad\.yml: malformed YAML"):
        load_documents(
            read_event_file(tmp_path, "reviews/bad.yml"),
            where="reqharness/reviews/bad.yml",
        )

    (pending / "bad.yml").write_text("change: [unclosed\n", encoding="utf-8", newline="\n")
    with pytest.raises(ValidationError, match=r"pending/bad\.yml: malformed YAML"):
        load_documents(
            read_event_file(tmp_path, "pending/bad.yml"),
            where="reqharness/pending/bad.yml",
        )


def _two_admins(root: Path) -> None:
    """bob plus ana as a second admin (ana added to the config, then granted
    admin by bob in one event) — the prerequisite for pending approvals."""
    _seed(root)
    _add_ana(root)
    assert propose(
        root, requester="bob", action="grant",
        person="ana", role="admin", now=T2,
    ) is None


def test_pending_request_resolved_once(tmp_path):
    """RHFIX4 H1: a pending request resolves AT MOST ONCE — before appending,
    the verified chain is scanned for an event already referencing the
    request's digest.  A double approve, a reject-after-approve and an
    approve-after-reject are all refused `request already resolved` and
    leave roles.yml byte-identical."""
    _two_admins(tmp_path)
    held = propose(
        tmp_path, requester="bob", action="grant",
        person="bob", role="req-reviewer", now=T3,  # a self-change: pending
    )
    assert held is not None

    # approve lands once...
    approve_pending(tmp_path, pending=held.name, approver="ana", now=T4)
    approved_bytes = (tmp_path / ROLES).read_bytes()
    # ...a second approve is refused, and so is a reject after the approve
    with pytest.raises(ValidationError, match="request already resolved"):
        approve_pending(tmp_path, pending=held.name, approver="ana", now=T5)
    with pytest.raises(ValidationError, match="request already resolved"):
        reject_pending(tmp_path, pending=held.name, approver="ana", now=T6)
    assert (tmp_path / ROLES).read_bytes() == approved_bytes  # nothing appended
    report = verify_chain(tmp_path)
    assert report.ok
    assert effective_roles(report)["bob"] == ("admin", "req-reviewer")

    # the mirror arm: reject lands once, then the approve is refused
    held2 = propose(
        tmp_path, requester="ana", action="grant",
        person="ana", role="req-reviewer", now=T5,  # a self-change: pending
    )
    reject_pending(tmp_path, pending=held2.name, approver="bob", now=T6)
    with pytest.raises(ValidationError, match="request already resolved"):
        approve_pending(tmp_path, pending=held2.name, approver="bob", now=T7)
    report = verify_chain(tmp_path)
    assert report.ok


def test_pending_resolution_refuses_name_content_mismatch(tmp_path):
    """RHFIX4 M1/M2: approve/reject run the read side's ONE shared validator
    (`pending.load_pending`, lazily imported — pending.py imports chain, so
    a module-level import would close a cycle).  A pending file whose name
    does not match its canonical content (R22) is refused by name, never
    resolved under a mismatched name."""
    _two_admins(tmp_path)
    held = propose(
        tmp_path, requester="bob", action="grant",
        person="bob", role="req-reviewer", now=T3,
    )
    assert held is not None
    tampered = held.parent / "tampered.yml"
    tampered.write_bytes(held.read_bytes())  # valid bytes, wrong name
    roles_bytes = (tmp_path / ROLES).read_bytes()
    with pytest.raises(ValidationError, match="name/content mismatch"):
        approve_pending(tmp_path, pending="tampered.yml", approver="ana", now=T4)
    with pytest.raises(ValidationError, match="name/content mismatch"):
        reject_pending(tmp_path, pending="tampered.yml", approver="ana", now=T4)
    assert (tmp_path / ROLES).read_bytes() == roles_bytes
    assert verify_chain(tmp_path).ok
def test_pending_write_refuses_link_and_writes_nothing_outside(tmp_path):
    """SEC F3 (DDR follow-up): `_write_pending` confines-then-creates, exactly
    like `reviews.record_review` — a link or junction at
    `reqharness/pending` (or any parent component) is refused BY NAME before
    anything is written, and nothing reaches through the link: roles.yml is
    byte-identical and the link target stays empty."""
    import os

    outside = tmp_path / "outside"
    outside.mkdir()
    repo = tmp_path / "repo"
    repo.mkdir()
    _seed(repo)
    junction = repo / "reqharness" / "pending"
    try:
        if os.name == "nt":
            subprocess.run(
                ["cmd", "/c", "mklink", "/J", str(junction), str(outside)],
                check=True, capture_output=True,
            )
        else:
            junction.symlink_to(outside, target_is_directory=True)
    except (OSError, subprocess.CalledProcessError):
        pytest.skip("link creation is unavailable on this host")

    roles_bytes = (repo / ROLES).read_bytes()
    with pytest.raises(
        ValidationError, match=r"pending/\d{8}-[0-9a-f]{8}\.yml: refused \(link\)"
    ):
        propose(
            repo, requester="bob", action="grant",
            person="bob", role="req-reviewer", now=T2,
        )
    assert (repo / ROLES).read_bytes() == roles_bytes  # nothing appended
    assert list(outside.iterdir()) == []  # nothing written through the link


def test_roles_append_lock_repairs_newline_and_refuses_stale_lock(tmp_path):
    """SEC F4 (DDR follow-up): every roles.yml append runs under the
    exclusive lock `reqharness/.roles.lock` (O_CREAT|O_EXCL, removed in
    finally, head re-verified under the lock).  A file whose last byte is
    not a newline is repaired with a prepended newline — the new document
    parses, the chain verifies.  A present lock is a NAMED refusal:
    roles.yml is unchanged and the stale lock is never deleted silently."""
    _seed(tmp_path)
    _add_ana(tmp_path)
    path = tmp_path / ROLES

    # arm 1: a truncated tail (no trailing newline) is repaired, not glued
    text = path.read_text(encoding="utf-8").rstrip("\n")
    path.write_text(text, encoding="utf-8", newline="\n")
    assert propose(
        tmp_path, requester="bob", action="grant",
        person="ana", role="req-reviewer", now=T2,
    ) is None
    docs = _read_docs(tmp_path)
    assert len(docs) == 3  # genesis, policy, grant — the append parsed
    assert verify_chain(tmp_path).ok
    assert not (tmp_path / "reqharness" / ".roles.lock").exists()  # removed

    # arm 2: a present lock refuses by name; the file and the lock stay put
    lock = tmp_path / "reqharness" / ".roles.lock"
    lock.write_text("stale\n", encoding="utf-8", newline="\n")
    roles_bytes = path.read_bytes()
    with pytest.raises(ValidationError, match=r"append lock held"):
        propose(
            tmp_path, requester="bob", action="grant",
            person="ana", role="admin", now=T3,
        )
    assert path.read_bytes() == roles_bytes
    assert lock.exists()  # never deleted silently


def test_request_resolving_event_needs_alien_approver(tmp_path):
    """SEC F5 (DDR follow-up): the chain walk enforces approver != requester
    on a `grant`/`revoke` carrying a `request_hash` (a pending-derived
    approval) — the API-level check in `approve_pending` is the first line,
    but a HAND-CRAFTED event must fail the walk the same way.  Arm 1: such
    an event appended on the head fails verify (`config changed without
    approval`) and the grant never lands.  Arm 2: the same shape as a fork
    child can never be legitimized by `resolve` — the API refuses it, a
    hand-written resolve fails verify `chain broken` (mutant M-F5 removes
    the requester arm of `_passes_approval` and both arms verify clean)."""
    # arm 1: a forged pending-derived grant on the head
    _seed(tmp_path)
    _add_ana(tmp_path)
    head = verify_chain(tmp_path).events[-1].this_hash
    forged = _event(
        head, 3, time=T2, action="grant",
        requested_by="bob", approved_by="bob",
        person="ana", role="req-reviewer",
        note="the requester approved their own request",
    )
    forged["request_hash"] = "ab" * 32
    forged["this_hash"] = chain_hash(
        head, {k: v for k, v in forged.items() if k != "this_hash"}
    )
    _append_raw(tmp_path, forged)
    report = verify_chain(tmp_path)
    assert not report.ok
    assert report.status == "config changed without approval"
    assert effective_roles(report) == {"bob": ("admin",)}  # the grant never lands

    # arm 2: the same shape as a fork child, with a resolve trying to
    # legitimize it
    forked = tmp_path / "forked"
    _seed(forked)
    _add_ana(forked)
    assert propose(
        forked, requester="bob", action="grant",
        person="ana", role="admin", now=T2,
    ) is None  # ana holds admin at the fork's bound head
    base = _read_docs(forked)
    head = base[-1]["this_hash"]
    child_a = _event(
        head, 4, time=T3, action="grant",
        requested_by="ana", approved_by="ana",
        person="bob", role="req-reviewer",
        note="ana requested and approved it herself",
    )
    child_a["request_hash"] = "cd" * 32
    child_a["this_hash"] = chain_hash(
        head, {k: v for k, v in child_a.items() if k != "this_hash"}
    )
    child_b = _event(
        head, 4, time=T3, action="grant",
        requested_by="bob", approved_by="bob",
        person="ana", role="req-reviewer", note="branch B",
    )
    _write_docs(forked, [*base, child_a, child_b])
    assert verify_chain(forked).status == "chain forked at seq 4"
    with pytest.raises(ValidationError, match="approval rule"):
        append_resolve(
            forked, approved_by="bob",
            chosen_hash=child_a["this_hash"],
            excludes_hash=child_b["this_hash"], now=T4,
        )
    resolve = _event(
        child_a["this_hash"], 5, time=T4, action="resolve",
        requested_by="bob", approved_by="bob", person="", role="",
        note="legitimize the self-approved child",
        resolve_excludes=child_b["this_hash"],
    )
    _append_raw(forked, resolve)
    report = verify_chain(forked)
    assert report.status == "chain broken"
