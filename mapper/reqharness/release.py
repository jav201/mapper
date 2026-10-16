"""Release-rule evaluation with the hard-coded mandatory rules (HLR-RH.7).

The evaluator ANDs the three MANDATORY rules — hard-coded in the core, never
removable through config (R1):

    chain_verified    roles.yml verifies clean AND the live config matches
                      the newest verified policy event's ``config_hash``
    policy_verified   the policy check above (the two travel together: a
                      chain that verifies with a mismatched policy is in
                      ``config changed without approval``)
    signers_in_force  every closing review was signed by a holder of the
                      class's reviewer_role at its BOUND HEAD — structural
                      in the derivation: only qualifying reviews close, and
                      an unknown recorded head makes the registry
                      `not verifiable`

then every rule declared in ``config.yml`` (config MAY add rules, never
remove the mandatory three — R1).  Verdicts are exact strings (LLR-RH.7.1):
``ready``, or ``not ready · <reason>``; a chain/policy break or an unknown
bound head yields EXACTLY ``not ready · registry not verifiable``; an
unentitled review alone never blocks the release (R5).

``safe_verify`` is the seam the release evaluation and ``--audit`` share:
a schema ValidationError from a tampered or hand-added document (e.g. a
hand-added genesis lacking ``config_hash``) becomes the status
``chain broken`` — or ``config changed without approval`` when the refusal
names the config — never an exception escaping the evaluation.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from mapper.reqharness.chain import (
    STATUS_BROKEN,
    STATUS_TAMPERED,
    ChainReport,
    verify_chain,
)
from mapper.reqharness.config import CONFIG_NAME, REQHARNESS_DIR
from mapper.reqharness.derive import STATE_REVIEWED, STATE_RETIRED, Derivation
from mapper.reqharness.records import Config, ValidationError

VERDICT_READY = "ready"
VERDICT_NOT_VERIFIABLE = "not ready · registry not verifiable"
REASON_UNREVIEWED = "unreviewed requirements"

RULE_CHAIN = "chain_verified"
RULE_POLICY = "policy_verified"
RULE_SIGNERS = "signers_in_force"
RULE_ALL_REVIEWED = "all_active_reviewed"
RULE_AUTHORS_DECLARED = "authors_declared"

#: The mandatory three — config may ADD, never remove (R1).
MANDATORY_RULES = (RULE_CHAIN, RULE_POLICY, RULE_SIGNERS)

_CONFIG_WHERE = f"{REQHARNESS_DIR}/{CONFIG_NAME}"


def safe_verify(repo: str | Path) -> ChainReport:
    """``verify_chain`` with the schema-refusal ladder folded INTO the
    status words: a ``ValidationError`` from a tampered or hand-added
    document (a hand-added genesis lacking ``config_hash`` lands there)
    becomes ``chain broken`` — or ``config changed without approval``
    when the refusal names the config — never an exception escaping
    ``--audit`` or the release evaluation."""
    try:
        return verify_chain(repo)
    except ValidationError as exc:
        where = str(exc)
        if where.startswith(_CONFIG_WHERE) or f": {_CONFIG_WHERE}" in where:
            return ChainReport(status=STATUS_TAMPERED, events=())
        return ChainReport(status=STATUS_BROKEN, events=())


@dataclass(frozen=True)
class Verdict:
    """The release verdict: the exact text plus the per-rule results —
    the mandatory three first, then the config rules in config order, so
    a silently skipped rule (M-RL1) is observable."""

    ready: bool
    text: str
    rules: tuple[tuple[str, bool], ...]

    def rule(self, rule_id: str) -> bool:
        """One rule's result; False when the rule was never evaluated."""
        return dict(self.rules).get(rule_id, False)


def evaluate(config: Config, report: ChainReport, derivation: Derivation) -> Verdict:
    """AND the mandatory rules, then every config-declared rule (R1)."""
    if not report.ok or not derivation.verifiable:
        # The exact block (LLR-RH.7.1): a broken chain, a policy mismatch
        # or an unknown recorded head — never a per-rule reason.
        return Verdict(
            ready=False,
            text=VERDICT_NOT_VERIFIABLE,
            rules=(
                (RULE_CHAIN, report.ok),
                (RULE_POLICY, report.policy_ok),
                (RULE_SIGNERS, derivation.verifiable),
            ),
        )
    active_reviewed = all(
        state == STATE_REVIEWED
        for state in derivation.states.values()
        if state != STATE_RETIRED  # retired objects are excluded (R5)
    )
    # `authors_declared` (HLR-RS.5 / F2): fails when any ACTIVE object's
    # owning batch is blank or absent from the config `authors` map — the
    # derivation reports those objects in `authors_missing` by id.
    authors_declared = not derivation.authors_missing
    known = {
        RULE_CHAIN: report.ok,
        RULE_POLICY: report.policy_ok,
        RULE_SIGNERS: derivation.verifiable,
        RULE_ALL_REVIEWED: active_reviewed,
        RULE_AUTHORS_DECLARED: authors_declared,
    }
    rules: list[tuple[str, bool]] = [(rule, known[rule]) for rule in MANDATORY_RULES]
    for declared in config.release_rules:
        if declared.id in known:
            rules.append((declared.id, known[declared.id]))
        else:
            # A config-declared rule the core does not implement is a named
            # failure, never a silent skip.
            rules.append((declared.id, False))
            return Verdict(
                ready=False,
                text=f"not ready · unknown release rule {declared.id!r}",
                rules=tuple(rules),
            )
    failed = next((rule for rule, ok in rules if not ok), None)
    if failed is None:
        return Verdict(ready=True, text=VERDICT_READY, rules=tuple(rules))
    reason = REASON_UNREVIEWED if failed == RULE_ALL_REVIEWED else failed
    return Verdict(ready=False, text=f"not ready · {reason}", rules=tuple(rules))


__all__ = [
    "MANDATORY_RULES",
    "REASON_UNREVIEWED",
    "RULE_ALL_REVIEWED",
    "RULE_AUTHORS_DECLARED",
    "RULE_CHAIN",
    "RULE_POLICY",
    "RULE_SIGNERS",
    "VERDICT_NOT_VERIFIABLE",
    "VERDICT_READY",
    "Verdict",
    "evaluate",
    "safe_verify",
]
