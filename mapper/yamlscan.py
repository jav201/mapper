"""The one YAML prescan: refuse an anchor, an alias or over-deep nesting BEFORE any compose.

Extracted from `MapStore._prescan_sidecar` (LLR-RML.1.4, ARQ R-017) so `store` and
`relmap` share one definition of the rule without either importing the other.  This module
reads no file and holds no operator-facing wording: it raises a typed error carrying the
facts, and each caller words its own refusal (so each surface keeps its text byte for byte).

`yaml.parse` is a state machine with an explicit stack: the scan never recurses, so a
10,000-nesting document is a typed refusal in milliseconds, never a `RecursionError`, and an
anchor-amplified document is stopped before `yaml.safe_load` could materialise it (M-Q2-1).
"""
from __future__ import annotations

import yaml

from .osopen import MAX_DEPTH

#: An anchor NAME is attacker-controlled document content: a refusal carries at most this many
#: characters of it, then an ellipsis (review inc003-F1; LLR-N13.1.7: a coordinate that carries a
#: value behaves like a value).
ANCHOR_NAME_DISPLAY = 40


class YamlLimitError(Exception):
    """The first anchor/alias (`kind == "anchor"`) or nesting past MAX_DEPTH (`kind == "depth"`).

    Deliberately NOT a `ValueError` or `yaml.YAMLError`: the callers' parser nets catch those
    and would rewrite the typed refusal to "unreadable" (M-RML-12).  `shown` is the anchor name
    cut at ANCHOR_NAME_DISPLAY plus an ellipsis when cut (empty for depth); `limit` is MAX_DEPTH.
    """

    def __init__(self, kind: str, shown: str, limit: int) -> None:
        super().__init__(kind)
        self.kind = kind
        self.shown = shown
        self.limit = limit


def prescan(text: str) -> None:
    """Raise `YamlLimitError` for the first anchor/alias event or for nesting past MAX_DEPTH.

    A `yaml.YAMLError` from `yaml.parse` propagates to the caller's parser net.
    """
    depth = 0
    for event in yaml.parse(text):
        anchor = getattr(event, "anchor", None)
        if anchor is not None:
            shown = anchor[:ANCHOR_NAME_DISPLAY]
            if len(anchor) > ANCHOR_NAME_DISPLAY:
                shown += "…"
            raise YamlLimitError("anchor", shown, MAX_DEPTH)
        if isinstance(event, (yaml.SequenceStartEvent, yaml.MappingStartEvent)):
            depth += 1
            if depth > MAX_DEPTH:
                raise YamlLimitError("depth", "", MAX_DEPTH)
        elif isinstance(event, (yaml.SequenceEndEvent, yaml.MappingEndEvent)):
            depth -= 1
