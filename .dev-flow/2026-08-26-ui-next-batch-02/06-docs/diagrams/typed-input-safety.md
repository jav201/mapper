# Typed-input safety flow — mapper — Batch 2026-08-26-ui-next-batch-02

> Phase 6 diagram. Every node that names code names a real symbol at HEAD `46e190b` (grep-verified). Owner role: `docs-writer` — drafted by `deepseek-v4-pro`, verified by the orchestrator.

```mermaid
flowchart TD
    A["typed text (repo / path / map id)"] --> B{"classify"}
    B -- "repo spec" --> C["mapper/github.py::_classify"]
    C --> D{"_is_url on the closed allow-list?"}
    D -- "yes (https / git@)" --> E["clone / fetch (pinned git env)"]
    D -- "no (dash URL, userinfo, extra slashes, UNC…)" --> R["_refuse_unsafe → refusal sentence"]
    B -- "local path" --> F["mapper/osopen.py::safe_local_path"]
    F --> G{"confine_reason: lexical checks"}
    G -- "drive letter / .. / colon / DOS device / link / stream suffix / lone surrogate" --> R
    G -- "inside workspace, real folder" --> H["open_external → launcher"]
    B -- "map id" --> I["mapper/store.py::check_map_id"]
    I -- "empty / separator / .. / drive / : / device / trailing dot-space" --> R
    I -- "valid id" --> J["create (never overwrites)"]
    R --> K["operator sees refusal, nothing opened / written / run"]
```

Two independent, closed allow-lists — one for URLs (`mapper/github.py`), one for paths (`mapper/osopen.py`) — plus a map-id confinement in the store. A refused input is refused **before any filesystem call or subprocess runs**; the refusal surfaces as a sentence (`refusal_sentence`) rather than a raw exception.
