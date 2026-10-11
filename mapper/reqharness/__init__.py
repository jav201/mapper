"""ReqHarness — the headless domain core for dev-flow's human-auditable artifacts.

This package owns the entire ReqHarness domain: typed configuration with a
policy-bound genesis, the hash-chained role log, review/pending stores, derived
object states, baselines, release-rule evaluation and the read-only audit
entry.  It is HEADLESS (docs/ARCHITECTURE.md §3): stdlib + PyYAML only, plus
the one sanctioned `mapper.osopen` containment edge — no Textual, no Rich, no
network.  Screens and the CLI consume it; nothing here knows about the TUI.
"""
