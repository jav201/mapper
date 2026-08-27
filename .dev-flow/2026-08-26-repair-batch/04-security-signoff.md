# Security Sign-off — `fix/shipped-defects-repair` (whole branch diff vs `origin/master`)

Reviewer: security-reviewer · Date: 2026-08-27
Base: `origin/master` @ `d6b60e6b4f18b10123fffc76bbb36891473df653`
Tree state: nothing committed, nothing staged — the batch is entirely working-tree.

---

## BLUF — verdict

**CLEAR TO MERGE.**

No HIGH finding. The markup-injection control (C-17) that triggered family C is **sound at every sink that can actually carry hostile file-derived text**, and I verified it by rendering a hostile node id end-to-end through the real screens rather than by reading the source. The batch is a net security improvement over `origin/master` on every axis I measured.

Five MEDIUM findings follow. None is a vulnerability; all are gate-integrity or containment issues. **M1 and M2 are the two I would fix before merge** — M1 because it is the third recurrence of the same "defense present, nothing asserts it" pattern that two prior reviews already caught, and M2 because it is a live defect this batch introduced that defeats the batch's own stated requirement LLR-R03.5.

---

## Threat model for this diff

The attacker is **a malformed or hostile file the operator opens**: a `.mmd` map, its `_nodos.yml` sidecar, or an imported CSV. There is no network attacker, no multi-tenant boundary, no auth surface, and no deploy surface in this diff. Everything runs locally under the operator's own privileges on their own files.

Realistic goals available to such a file:

1. **Rewrite what the operator reads.** A notice like `campo ilegible: <node_id>.<key>` interpolates two file-derived coordinates. If that string reaches a markup-parsing sink, the file controls the rendered text — it can delete the very node id the operator needs in order to find and repair the fault. This is the primary threat and the reason C-17 exists.
2. **Kill or freeze the app.** A cycle or pathological depth reaching a renderer inside the message pump.
3. **Deny a map permanently.** A single hostile scalar making an otherwise good map unopenable.
4. **Escape the workarea.** File-derived text becoming a filesystem path.

Goal 1 is defended and proven. Goal 2 is defended (findings M4 bounds the residual). Goal 3 is **achievable today** — finding M2. Goal 4 is not reachable through anything this diff changed.

Non-threat, explicitly: the operator typing a hostile map name at a prompt. They already have full local privilege; a `[` in a typed name is a cosmetic toast defect, not a security boundary. Sinks in that class are recorded as LOW, not MEDIUM.

---

## The notify/markup sink census

`App.notify` defaults to `markup=True` in Textual 8.2.8, and `darkside.plain()` (`mapper/darkside.py:276-287`) strips control bytes but **deliberately preserves markup** — its own docstring says so. So `markup=False` is the entire defense at each sink.

I derived this set myself rather than trusting the count of three: `grep -rn "notify(" mapper/` returns **30 call sites**, which I classified by whether the interpolated text can originate in a file.

First, the threat is real — not theoretical. Markup parsing **silently rewrites** the text:

```
--- PROBE 1: is markup=True actually dangerous? ---
raw warning text      : 'campo ilegible: ev[bold red]il[/]x[nonsense.k'
darkside.plain output : 'campo ilegible: ev[bold red]il[/]x[nonsense.k'
plain() PRESERVES markup: True
markup-parsed .plain  : 'campo ilegible: evilx[nonsense.k'
TEXT WAS REWRITTEN    : True
```

The node id the operator needs (`ev[bold red]il[/]x`) becomes `evilx`. The fault becomes unfindable.

### Sinks that CAN receive file-derived text

| # | Site | Message | `markup=False`? | Asserted by |
|---|------|---------|-----------------|-------------|
| 1 | `mapper/app.py:453` | `no se pudo cargar {name}: {exc}` — `HomeScreen.load_or_notice`, **failure** branch | **YES** | **YES** — `tests/test_repair_cycles.py:327` |
| 2 | `mapper/app.py:460` | `{name}: {load_warnings}` — `load_or_notice`, **warning** branch | **YES** | **YES** — `tests/test_repair_fields.py:428` (TC-R20c) |
| 3 | `mapper/app.py:1155` | `{load_warnings}` — `MapScreen._notice_load_warnings` | **YES** | **YES** — `tests/test_repair_fields.py:385` (TC-R20) |
| 4 | `mapper/app.py:1180` | `error cargando mapa: {plain(str(e))}` | **YES** | **NO** — see **M1** |
| 5 | `mapper/app.py:1455` | `{status}: {shown}` — attachment path from sidecar | **YES** | **NO** — see **M1** |
| 6 | `mapper/app.py:760` | `no se pudo guardar: {e}` — `_ImportPreviewScreen.action_save` | **NO** | n/a — see **M3** |
| 7 | `mapper/app.py:687` | `no se pudo leer CSV: {e}` | **NO** | n/a — LOW (L3) |
| 8 | `mapper/app.py:1738` | `exportación fallida: {e}` | **NO** | n/a — LOW (L3) |
| 9 | `mapper/screens/factory.py:470` | `no se pudo generar: {exc}` | **NO** | n/a — LOW (L3) |
| 10 | `mapper/app.py:1055`, `:1058` | `{exc}` from `GitHubError` — **remote**-derived, not file | **NO** | n/a — LOW (L3) |

Sites 1–3 are the three the batch set out to defend, and all three are correct **and** armed. Sites 4 and 5 carry the keyword but nothing asserts it (M1). Site 6 is the fourth file-derived sink and lacks the keyword entirely (M3).

### Sinks that cannot receive file-derived text

`app.py:647, 661, 672, 682, 1053, 1530, 1632, 1638, 1646, 1743, 1749, 1778, 1820` and `factory.py:423, 427, 444, 457, 461, 468` — literal strings, integers, or operator keystrokes. `app.py:1820` passes `markup=False` over a pure literal. Recorded as LOW (L3) where they interpolate anything at all.

### Rich `Text` construction paths — clean

`HelpScreen._render_keymap` (`mapper/screens/help.py:80-90`) uses `Text.assemble` over `bindings_for(self.scope)`. `scope` comes from `KEY_SCOPE` class constants (`SCOPE_HOME/MAP/IMPORT/...`), and glyphs and labels come from the in-code bindings registry. **No file-derived text reaches the help overlay at all**, so the S-08 fix (`VerticalScroll` + `height: 1fr`) introduces no markup surface. `Static(f"atajos · {self.scope}")` is a markup-parsed sink but `scope` is a code constant.

`darkside.Text.assemble` in the two new renderer fallbacks (`app.py:737-740`, `app.py:1358-1361`) wraps exception text in a `Text` object with explicit styles — `Text` does not parse markup, so these are safe by construction, which is exactly the invariant `plain()`'s docstring relies on.

### Verified end-to-end, not by reading

A sidecar carrying the node id `ev[bold red]il[/]x[nonsense` (a well-formed opening tag, a closing tag, and an unmatched bracket at once) with an unreadable field, driven through the real `MapScreen` and `HomeScreen`:

```
--- PROBE 3: HomeScreen.load_or_notice (warning branch) ---
  msg   = 'm: campo ilegible: ev[bold red]il[/]x[nonsense.k'
  kwargs= {'title': '', 'severity': 'warning', 'markup': False}
  -> literal, markup=False, screen alive: PASS
```

The hostile id renders **verbatim** — not escaped (no visible backslashes), not parsed away — and the screen survives. Probe 4 repeated this with **no stub at all**, letting the real Textual toast render: `screen alive = MapScreen`, textual 8.2.8. The defense holds at the widget, not just at the call site.

---

## Findings

### M1 — Two `markup=False` keywords that no test asserts [MEDIUM]

- **What:** `app.py:1180` (`error cargando mapa`) and `app.py:1455` (attachment status) both pass `markup=False` over file-derived text, and **no test observes the keyword**. The defense can be deleted and the suite stays green.
- **Where:** `mapper/app.py:1180`, `mapper/app.py:1455`. Root cause is the stub shape: `tests/test_repair_cycles.py:372` and `:240` use `lambda msg, **kw: notices.append(str(msg))` — kwargs captured and **discarded**. The three armed sinks use `notices.append((str(msg), kw))`.
- **Evidence — proven by mutation on a copy** (repo untouched). Dropped `markup=False` at both sites, ran the full suite against a clean copy and the mutated copy under identical conditions:

```
=== diff clean vs mutated failure sets ===
>>> IDENTICAL: the M1+M2 mutation reddened NOTHING <<<
clean failures: 28  mutated failures: 28
```

(The 28 are a git-absence artifact of the temp dir — the `test_c53_*` tests compare against master and need `.git`. In the real repo all 409 pass. The point is the two runs are *identical*.)

- **Why it matters:** This is the **third recurrence** of one pattern. Increment 3's review found a sink with the keyword unasserted; the re-gate found a third; this pass finds two more. Each time the code was correct and nothing said so. `app.py:1180` is the sink that fires on every failed load — the highest-traffic file-derived notice in the app.
- **Recommendation:** Change the two stubs to capture kwargs and assert, exactly as the three armed sinks do:
  ```python
  notices: list[tuple[str, dict]] = []
  app.notify = lambda msg, **kw: notices.append((str(msg), kw))
  ...
  hits = [(m, kw) for m, kw in notices if "error cargando mapa" in m]
  assert hits, notices
  assert all(kw.get("markup") is False for _, kw in hits), hits
  ```
  `hits` must be asserted non-empty **before** the `all(...)`, since `all()` over an empty list is vacuously true — the batch already gets this right at `test_repair_cycles.py:325-327`.

### M2 — A hostile sidecar scalar denies the whole map, defeating LLR-R03.5 [MEDIUM]

- **What:** `_coerce_field` calls `str(value)` on YAML scalars. Python 3.12 caps integer→string conversion at 4300 digits, so a sidecar integer longer than that makes `str()` raise `ValueError` — an exception `_coerce_field` neither catches nor records. It propagates out of `_graph_from_sidecar` and out of `MapStore.load` as a bare `ValueError`, **not** a `MapStoreError`.
- **Where:** `mapper/store.py:51-52` (`if isinstance(value, _SCALARS): return str(value)`).
- **Evidence — executed** against a real sidecar with a 5000-digit field:

```
=== D: a sidecar carrying a 5000-DIGIT integer field (str() limit is 4300) ===
  load() RAISED ValueError: Exceeds the limit (4300 digits) for integer string conversion: value has 5000 digits
  -> the screens' `except Exception` sinks turn this into a notice
```

- **Why it matters:** LLR-R03.5 is the batch's own promise that *a malformed field never denies the map* — the whole point of S-02's repair is that one bad field becomes a warning and the map still opens. Here one scalar denies the entire map. It degrades **safely** (increment 1's sink-class `except Exception` guards catch it and show a notice rather than crashing, so S-01's fix is doing its job), and it is strictly better than `master`, which passed the raw int through to break every downstream consumer. But the stated guarantee does not hold.
- **Recommendation:** Treat a failed coercion as an unreadable field — the branch already exists for containers:
  ```python
  if isinstance(value, _SCALARS):
      try:
          return str(value)
      except ValueError:
          graph.load_warnings.append(f"campo ilegible: {node_id}.{key}")
          return ""
  ```

### M3 — A fourth file-derived notify sink with no `markup=False` [MEDIUM]

- **What:** `_ImportPreviewScreen.action_save` catches the new `MapStoreError` cycle refusal into a bare f-string with markup parsing on. `MapStoreError`'s message interpolates node ids.
- **Where:** `mapper/app.py:760` — `self.notify(f"no se pudo guardar: {e}", severity="error")`. This is the **only** call site of the eight `store.save` sites where a cyclic graph can actually arrive: `MapScreen` refuses cyclic maps at load, and the app has no reparent operation (`add_edge` at `app.py:1767` only ever attaches a freshly-generated id), so the in-memory graph cannot become cyclic through the UI.
- **Evidence — NOT exploitable today, proven by execution.** `preview_csv` slugifies ids, and `slugify` (`mapper/mermaid.py:45-50`) collapses everything outside `[\w\s-]` to a hyphen:

```
--- PROBE 5: import-preview save sink ---
  node ids after slugify = ['a-bold-red-x', 'b', 'c-y']
  find_cycle()           = ['a-bold-red-x', 'b', 'c-y', 'a-bold-red-x']
  save() raised          = MapStoreError('el mapa tiene un ciclo: a-bold-red-x→b→c-y→a-bold-red-x')
  message contains '['   = False
```

The `.mmd` route is constrained the same way — `_MERMAID_EDGE`/`_MERMAID_NODE` match ids as `[\w-]+`. So the cycle message **cannot** carry markup from either route.
- **Why it matters:** The defense is real but it lives in a *different module* (`mermaid.slugify`) and is a side effect of mermaid-id hygiene, not a stated security control. Nothing records the dependency, and nothing would redden if slugify were relaxed to permit brackets.
- **Recommendation:** Add `markup=False` and `darkside.plain(str(e))` for consistency with the other four file-derived sinks. One line, no behaviour change today, and it removes the cross-module coupling.

### M4 — `MAX_RENDER_NODES = 12000` admits ~50 s of frozen UI [MEDIUM]

- **What:** The new node cap is calibrated well above the point at which `LayeredRenderer` becomes unusable. Render cost is O(n²), measured.
- **Where:** `mapper/views/layered.py:14` (also `outline.py`, `radial.py`).
- **Evidence — measured on the branch:**

```
MAX_RENDER_NODES = 12000
  n=   500 -> 0.07s      n=  4000 -> 5.23s
  n=  1000 -> 0.27s      n=  8000 -> 22.58s
  n=  2000 -> 1.08s
```

Clean 4× per 2× — quadratic. Extrapolated to the cap: ~50 s. An 11,000-node graph (under the cap) exceeded a 25 s probe bound. `refresh_canvas` runs inside the message pump, and its `try/except` cannot catch a slow loop.
- **Why it matters — and why it does not block:** This is a **net improvement**, not a regression. Benchmarked against `origin/master` under identical conditions:

```
master : MAX_RENDER_NODES: ABSENT (no cap)
  n= 1000 -> 0.46s   n= 2000 -> 1.78s   n= 4000 -> 7.17s
branch :
  n= 1000 -> 0.27s   n= 2000 -> 1.08s   n= 4000 -> 5.23s
```

The branch is ~1.4× faster (prebuilt `_child_index`/`_parent_index` replacing per-node `children_of`/`parent_of` rescans, plus the `body_h` clamp) **and** adds a cap where master had none — master would grind indefinitely on a 50,000-node map. The residual is a bounded, recoverable freeze on a pathological local file.
- **Recommendation:** Accept knowingly, or lower the cap to ~4000 (≈5 s worst case) if a frozen TUI is judged worse than a declared degradation. The `_degraded()` message already handles the refusal path gracefully.

### M5 — `-m 'not slow'` deselects the batch's own acceptance, and no CI lane exists [MEDIUM]

- **What:** `pyproject.toml` adds `addopts = "-m 'not slow'"`, whose own comment states *"CI must run `-m slow` as its own lane, because that lane is where HLR-R02's acceptance actually lives."* There is no CI.
- **Where:** `pyproject.toml:27-33`.
- **Evidence:**

```
$ ls -la .github/workflows/
ls: cannot access '.github/workflows/': No such file or directory
$ git ls-files | grep -i "github\|ci\|tox\|Makefile"
mapper/github.py
tests/test_github.py
```

Default run: `409 passed, 16 deselected`. The slow lane passes when invoked explicitly: `16 passed, 409 deselected in 28.69s`.
- **Why it matters:** The comment asserts a compensating control that does not exist in the repo. On a plain `pytest` — what a developer and any future gate runs — HLR-R02's depth-5000 acceptance silently does not run. The 16 tests are real and they pass; nothing routinely runs them.
- **Recommendation:** Either add the two-lane CI workflow the comment promises, or record in the batch docs that the slow lane is a manual pre-merge step and run it as part of the merge checklist. I ran it for this gate; it is green.

### LOW findings

- **L1 — `.env` is not gitignored.** `git check-ignore .env` returns no match. No `.env` exists today, so nothing is at risk, but there is no guard if one is created. Add `.env` and `.env.*` to `.gitignore`. (`mapper.db` and `*.db` **are** correctly covered — `.gitignore:8-9`, verified.)
- **L2 — Operator identity paths in `.dev-flow/**` artifacts.** ~48 occurrences of `C:\Users\jjgh8\...` across increment write-ups and, most heavily, the four `mutation-battery*.txt` logs. Two distinct leaks: the `harness :` header lines expose a scratchpad path including a **Claude session UUID**, and traceback tails expose `C:\Users\jjgh8\anaconda3\Lib\site-packages\...`. No secret values. Also `.dev-flow/2026-08-26-ui-next-batch-02/01b-ux-decisions.md:24` names the operator in a persona table. Scrub the username or exclude the raw `.txt` batteries from the commit.
- **L3 — Markup-parsing sinks over non-file text.** `app.py:647, 661, 682, 687, 1053-1058, 1738`; `factory.py:423, 444, 468, 470`. Operator-typed or remote-derived, so outside the primary threat model, but `app.py:1055/1058` interpolate `GitHubError` text that originates on a **remote** and is the closest of these to a real vector. Not introduced by this batch.
- **L4 — `_text_attributes()` recomputed per node.** `mapper/store.py:226` calls it inside the `for nid, ndata in nodes_data.items()` loop. Small constant, but it re-walks `Ficha.__dataclass_fields__` once per node. Hoist above the loop.
- **L5 — `_pop_snapshot` is unguarded against the batch's new raise.** `mapper/app.py:1531-1540` calls `_graph_from_sidecar` (can now raise `MermaidError`) and `store.save` (can now raise `MapStoreError`) with no `try/except`, inside an action handler. Currently unreachable — snapshots are built from an acyclic in-memory graph — but it is the one `save` call site whose safety rests on an invariant the batch just made load-bearing.

---

## What I verified and found sound

- **Nothing is staged.** `git diff --cached --stat` is empty; `git status --porcelain` shows the batch as unstaged working-tree changes only. **`prototypes/ui_next/` and `prototypes/ui_next2/` are untracked and not staged.** `mapper.db` is not tracked and is ignored by `.gitignore:9` (`*.db`), confirmed via `git check-ignore -v`. No HIGH on either count.
- **No secrets in production source.** Independent sweep of the tracked diff's added lines plus all untracked new files: zero API keys, tokens, passwords, private keys, connection strings, OAuth secrets, `.env` content, or credential-bearing URLs anywhere in the corpus. `mapper/` is clean on every pattern class. The four new test files use `tmp_path` throughout — no hardcoded paths.
- **`pyproject.toml` adds no dependencies and loosens no pins.** The 8 added lines are the pytest `slow` marker and `addopts`, nothing else. No supply-chain surface in this diff.
- **The YAML loader is `yaml.safe_load` — verified, not assumed.** `mapper/store.py:256`, `mapper/diff.py:54`, `mapper/app.py:1536`. No `yaml.load` anywhere. Alias-expansion ("billion laughs") is not effective: PyYAML shares references rather than deep-copying, and a 7-level alias nest loaded in 0.00 s.
- **Container refusal blocks a real resource-exhaustion path.** `_coerce_field` refuses lists and dicts **before** calling `str()`. The docstring justifies this on `coverage()` grounds, but it also happens to prevent `str()` on a deeply-aliased YAML structure from blowing up. Measured: a nested aliased list is refused in 0.001 ms with a warning recorded, never stringified. Good property, currently undocumented as such.
- **No renderer hangs on hostile input.** All three refuse a cycle with a clean `ValueError` rather than looping, and all three survive a depth-5000 chain and an over-cap graph:

```
=== Radial ===   cyclic -> raised ValueError: cycle through a: the graph is not a tree
                 depth-5000 chain -> returned    wide 12001 (over cap) -> returned
=== Layered ===  cyclic -> raised ValueError     depth-5000 -> returned    12001 -> returned
=== Outline ===  cyclic -> raised ValueError     depth-5000 -> returned    12001 -> returned
```

- **The hang-mode guard increment 3 flagged is gone, not merely bounded.** `Graph.resolve_document`'s parent recursion was deleted outright (`mapper/model.py:104-135`) rather than de-recursed, which removes the guard whose only failure mode was a hang. The one remaining unguarded parent-walk, `mapper/views/radial.py:172-175` (`while current is not None:` with no `seen` set), is **pre-existing and unchanged by this diff** (confirmed: context lines in `git diff`) and is unreachable because radial's own cycle refusal raises first — verified by executing it against a cyclic graph with a 10 s thread bound.
- **`Graph.find_cycle` is iterative and bounded.** `mapper/model.py:158-190` — explicit stack, `done` set, each node finished once and each edge traversed once. O(V+E). Correctly distinguishes a diamond from a cycle (only an edge back into the *active* path counts).
- **No path traversal introduced.** `_atomic_write` is **unchanged by this diff** (0 hits in `git diff -- mapper/store.py`). No file-derived value becomes a filesystem path in anything the batch touched; `map_id` reaches `workspace / f"{map_id}.mmd"` unsanitized but originates in operator keystrokes and is pre-existing behaviour. The one file-derived value that does become a path — `Attachment.path` via `open_external` — is untouched by this batch and already carries a comment acknowledging its sidecar origin (`mapper/osopen.py:38`); see residual risks.
- **No destructive commands and no deploy surface.** Nothing in the diff shells out, deletes recursively, force-pushes, drops a table, or deploys. `action_archive` gained a *stronger* guard (`app.py:1819-1825` refuses archiving the whole map, which previously wrote an empty map to disk with only an in-memory undo stack as recovery) — a genuine data-loss fix.
- **Both test lanes green in the real repo.** Default `409 passed, 16 deselected in 68.50s`; slow lane `16 passed, 409 deselected in 28.69s`. 425 tests total.

---

## Residual risks the operator should accept knowingly

1. **A pathological local map can freeze the TUI for up to ~50 s** (M4). Bounded, recoverable, and strictly better than shipped behaviour, but the cap is calibrated above the usable range.
2. **The slow lane is manual** (M5). Until CI exists, HLR-R02's depth-5000 acceptance runs only when someone types `-m slow`. It is green as of this gate.
3. **`Attachment.path` from a sidecar reaches `open_external`.** Out of scope for this diff — `osopen.py` is unchanged and the code already acknowledges the sidecar origin — but it remains the one place a file-derived string becomes something the OS launches. Worth its own review if attachments grow.
4. **The markup defense at `app.py:760` rests on `mermaid.slugify`** (M3), a constraint in another module that exists for mermaid-id hygiene rather than as a declared security control.
5. **`.dev-flow/**` artifacts carry operator identity and a Claude session UUID** (L2). Harmless in a private repo; scrub before any public push.
6. **No client data leaves the system.** This is a local-only TUI over local files; no LFPDPPP exposure in this diff. The only outbound surface is `mapper/github.py`, untouched here.

---

## Evidence checklist

- [x] Each finding has what · where · why · recommendation — all five MEDIUM and five LOW.
- [x] Each finding has a severity rating — 0 HIGH, 5 MEDIUM, 5 LOW.
- [x] No secret values appear in this output — none were found in production source; `.dev-flow` findings are cited by file:line and kind only.
- [x] Verdict is explicit — **CLEAR TO MERGE**, with M1/M2 recommended first.
- [x] New tool/integration scope and blast radius — **n/a, and verified n/a**: no MCP, Composio, n8n, or third-party connector is added; `pyproject.toml` adds zero dependencies.
- [x] Claims verified by execution, not reading — 5 probe modules, a mutation experiment against a clean control, a master-vs-branch benchmark, and both test lanes.

**No file in the repo was modified.** All probes, mutations, and the master baseline ran on copies under `C:\Users\jjgh8\AppData\Local\Temp\claude\...\scratchpad\`. This sign-off is the only file written.
