# Screen / key map — mapper — Batch 2026-08-26-ui-next-batch-02

> Phase 6 diagram. Every screen and `KEY_SCOPE` below is real at HEAD `46e190b`. Owner role: `docs-writer` — drafted by `deepseek-v4-pro`, verified by the orchestrator.

```mermaid
flowchart LR
    App["mapper/app.py (Textual)"] --> Home["HomeScreen (SCOPE_HOME)"]
    App --> Map["MapScreen (SCOPE_MAP)"]
    App --> Repo["RepoScreen (SCOPE_REPO)"]
    App --> Plug["connect-repo (SCOPE_PLUG)"]
    App --> Factory["FactoryScreen (SCOPE_FACTORY)"]
    App --> Settings["SettingsScreen (SCOPE_SETTINGS)"]
    App --> Help["HelpScreen (legend)"]

    Home -->|"j/k move · o/r/R pan · ? legend"| HomeKeys["home doors, per-map shape"]
    Map -->|"H/J/K/L pan · n/N/M walk · z fold · ? legend"| MapKeys["#map-canvas / #map-pagination / #map-rail"]
    Repo -->|"TEXT_ONLY_SCOPES → ? types"| RepoKeys["repo lane"]
    Plug -->|"TEXT_ONLY_SCOPES → ? types"| PlugKeys["typed repo text"]
    Factory -->|"s components"| FactoryKeys["templates"]
    Settings -->|"s components"| SettingsKeys["components sheet"]
    Help -->|"? opens · legend declares its own keys"| HelpKeys["view glyph vocabulary"]
```

- The seat is `mapper/keymap.py::bindings_for` / `groups_for_keybar`; every screen declares a `KEY_SCOPE` (`mapper/screens/factory.py::FactoryScreen.KEY_SCOPE`, `mapper/screens/settings.py::SettingsScreen.KEY_SCOPE`).
- `?` is a legend chord everywhere **except** text-field scopes, where it is a typed character (`A-135`, `A-137`, `TEXT_ONLY_SCOPES`).
- `MapScreen` owns pan (`pan_x`/`pan_y` on `ViewState`, `mapper/views/state.py`), search walk (`_walk_hits`), and overflow declaration (`_declare_after_layout`).
