# Security Review — `fix/repair-batch-02` (whole-branch merge gate)

| | |
|---|---|
| Batch | `2026-08-27-repair-batch-02` |
| Branch | `fix/repair-batch-02` @ `8675151` |
| Base ref | `d877784` (`origin/master`) |
| Reviewed | 2026-08-27 |
| Reviewer | `security-reviewer` (independent; did not author the change) |
| **Verdict** | **CLEARED TO MERGE — no HIGH finding.** 3 MEDIUM, 4 LOW. `F1` (~6 lines) and `F2`'s comment correction recommended for fold-in before merge — `F1` falsifies the batch's own declared threshold. |

---

## Scope reviewed

Working tree, uncommitted, against `d877784`:

| File | Status | Reviewed |
|---|---|---|
| `mapper/store.py` | MODIFIED (+189/−37) | full diff, plus the whole `load` / `_graph_from_sidecar` path in context |
| `docs/ARCHITECTURE.md` | MODIFIED (+31/−12) | full diff; every present-tense claim in the changed rows executed against disk |
| `tests/test_repair_store_boundary.py` | NEW | read + executed |
| `tests/test_repair_map_truth.py` | NEW | read + executed |
| `tests/test_repair_golden_census.py` | NEW | read + executed |
| `tests/test_repair_perf_shape.py` | NEW | read + executed |
| `.dev-flow/2026-08-27-repair-batch-02/**` | NEW | read for evidence integrity and secret content |

Also read as blast-radius context (unmodified): `mapper/app.py` (both `load` call sites and both `load_warnings` render sinks), `mapper/diff.py`, `mapper/darkside.py`, `mapper/model.py`, `pyproject.toml`, `.gitignore`.

No repo file was edited and no git mutation was run. All experiments ran in a scratch directory against a copy of the tree; the base-commit comparisons used `git show d877784:mapper/store.py` into scratch.

---

## Executive summary

This is a **good security batch**. Its central measurement reproduces exactly, the untrusted-input boundary is materially harder than it was at `d877784`, and the injection control the operator was most worried about (C-17) is genuinely armed at every reachable sink. I threw 24 hostile YAML shapes plus a YAML alias bomb at `_graph_from_sidecar` and got **zero** untyped escapes through it.

The findings are on the **edges** of the repair, not its core:

- The boundary hardening stops one line too late — `read_text` and the YAML parser sit *outside* the nets, and two untyped exception classes still escape `load` (`F1`).
- The two `except Exception` nets are justified by a caller contract that **does not exist in the tree**, and with zero logging in the package they permanently destroy the only diagnostic for a masked defect (`F2`). This is the trade the operator asked me to challenge independently; I do not accept it as recorded.
- The fix that made malformed attachments *loud* instead of *silent* introduced a measured ~19× warning-amplification DoS (`F5`), and the measurement that justified that design choice does not reproduce at the stated base (`F6`).

- The suite is fully green (517 passed) and the store's own test file survives mutation testing — but the one explicit *security control* in `load` has a test that cannot detect its removal (`F7`), and the doc-truth tests are narrower than the batch claims.

None of these is HIGH. Nothing here leaks a secret, grants a permission, reaches the network, or performs a destructive or irreversible action.

---

## Findings

### F1 — Untyped exceptions still escape `MapStore.load` — the net starts one line too late  ·  **[MEDIUM]**

**What.** `LLR-STO.1.1` threshold 3 and the comment at `mapper/store.py:419` claim that no non-`MapStoreError` escapes `load`. Two classes still do, both reachable from an ordinary workspace file.

**Where.**
- `mapper/store.py:382-383` — `read_text` is outside every `try`:
  ```python
  382:        mmd_text = mmd_path.read_text(encoding="utf-8")
  383:        yml_text = yml_path.read_text(encoding="utf-8") if yml_path.exists() else "{}"
  ```
- `mapper/store.py:386` — `except (yaml.YAMLError, ValueError)` does not cover `RecursionError`.

**Executed evidence.**

```
=== A. invalid UTF-8 in the sidecar / the .mmd (read_text is OUTSIDE any try) ===
[sidecar invalid utf-8] *** UNTYPED ESCAPE *** builtins.UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 23: invalid start byte
       at store.py:383 yml_text = yml_path.read_text(encoding="utf-8") if yml_path.exists() else "{}"
[mmd invalid utf-8]     *** UNTYPED ESCAPE *** builtins.UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 16: invalid start byte
       at store.py:382 mmd_text = mmd_path.read_text(encoding="utf-8")

=== B. parser-level recursion (deep nesting) ===
  depth=200:   [nested-200]   OK warnings=1 ['campo ilegible: a.k']
  depth=2000:  [nested-2000]  *** UNTYPED ESCAPE *** builtins.RecursionError: maximum recursion depth exceeded
       at scanner.py:425 self.fetch_flow_collection_start(FlowSequenceStartToken)
  depth=50000: [nested-50000] *** UNTYPED ESCAPE *** builtins.RecursionError: maximum recursion depth exceeded
```

The `RecursionError` payload is a **4 KB file** (`nodes.a.fields.k: [[[[…]]]]`, 2 000 deep). A third class, `OSError`/`PermissionError`, escapes the same way — see `F3`.

**Why it matters.** Contained, but real. Both product `load` callers happen to catch bare `Exception` (`mapper/app.py:450`, `mapper/app.py:1179`), so the screen does not die there — but that is luck, not design, and it is **not** what the code comment claims. The genuinely unguarded path is `mapper/diff.py:63`, where `store.load(map_id)` is called outside any `try`, and its caller `mapper/app.py:1636` (`diff = git_diff(...)`) is also unguarded — so an escape there reaches Textual's top level. Reachability is low (the map already loaded once to reach that screen) but non-zero: the file can change on disk, or lose read permission, between the two loads.

The larger issue is gate integrity: **threshold 3 is an acceptance criterion, the tests pass, and the criterion is not met as written.** That means the acceptance evidence does not cover what the requirement says.

**Recommendation.** ~6 lines. Pull the reads inside a net and widen the parser net. Recommended for `software-dev`, not applied by me:

```python
try:
    mmd_text = mmd_path.read_text(encoding="utf-8")
    yml_text = yml_path.read_text(encoding="utf-8") if yml_path.exists() else "{}"
except (OSError, UnicodeDecodeError) as exc:
    raise MapStoreError(
        f"no se pudo leer {map_id}: {type(exc).__name__}"
    ) from exc
try:
    sidecar = yaml.safe_load(yml_text) or {}
except (yaml.YAMLError, ValueError, RecursionError) as exc:
    ...
```

Note the message shape: `type(exc).__name__`, matching the `_reindex` net at `store.py:442` — which also closes `F3`.

*Same family, pre-existing, out of this batch's fence but worth folding in:* `mapper/store.py:530` (`last_session`) catches `(json.JSONDecodeError, OSError)` but not `UnicodeDecodeError`, and `mapper/diff.py:55` catches `yaml.YAMLError` but not `ValueError` — the exact gap `load` documents at `store.py:386-392`.

---

### F2 — The two `except Exception` nets rest on a caller contract that does not exist, and destroy the only diagnostic  ·  **[MEDIUM]**

*(This is the trade the operator asked me to challenge independently. I do not accept it as recorded.)*

**What.** Three separate problems in one construct.

**Where.** `mapper/store.py:418` and `mapper/store.py:436` (the two `# noqa: BLE001` nets).

**1. The stated premise is false.** `mapper/store.py:419-420` reads:

> `# LLR-STO.1.1 threshold 3.  Every caller in the product catches`
> `# `MapStoreError`; anything else escapes to the top level and kills the screen.`

Executed:

```
$ grep -rn "except MapStoreError" --include=*.py mapper/ | grep -v "^mapper/store.py"
(no output)
```

**Not one caller in the product catches `MapStoreError`.** The two real `load` callers catch bare `Exception`:

```
mapper/app.py:449:                graph = store.load(name)
mapper/app.py:450:            except Exception as exc:
mapper/app.py:1176:                self.base_graph = self.store.load(self.map_id)
mapper/app.py:1179:            except Exception as e:
```

Since both already catch `Exception`, **the nets change nothing about crash-resistance at any existing call site.** They change the *message* — which is a real UX win (a Spanish notice instead of `'int' object is not subscriptable`) — but that is a different and much smaller claim than the one recorded, and it is not the claim `LLR-STO.1.1` threshold 3 makes.

**2. The masked error is unrecoverable.** Confirmed there is no log to recover it from:

```
$ grep -rn "logging\." mapper/
$ echo "exit=$?"
exit=1
```

And the chain is never rendered:

```
=== does str(MapStoreError) expose the __cause__ chain at the sink? ===
  str(e)      = 'no se pudo leer la ficha de m: m_nodos.yml ilegible'
  e.__cause__ = AttributeError: 'int' object has no attribute 'get'
  cause text inside the string the operator sees? False
```

`raise … from exc` is correct and `__cause__` *is* populated — but both sinks render `str(e)` only (`mapper/app.py:454`, `mapper/app.py:1181`), and nothing logs or persists it. So a genuine code defect inside `_graph_from_sidecar` becomes permanently indistinguishable from a malformed file. **Detection is lost, not merely deferred** — which inverts the detection > prevention > recovery ordering this net is supposed to serve.

**3. The two nets are inconsistent with each other for no stated reason.** Net #2 (`store.py:442`) emits `type(exc).__name__`; net #1 (`store.py:430`) emits nothing. Same file, same class of masking, ten lines apart.

**What IS correct here** (verified, so the fix does not disturb it): `except MapStoreError: raise` correctly precedes `except Exception` in both nets (`store.py:416` before `:418`; `store.py:434` before `:436`), ordering is sound, `MermaidError` is handled ahead of both, and `raise … from exc` preserves the chain in every arm.

**Recommendation.** Keep the nets — the Spanish-message win is genuine — but make the masked type recoverable. Cheapest correct fix, one line, and it makes the two nets consistent:

```python
raise MapStoreError(
    f"no se pudo leer la ficha de {map_id}: {yml_path.name} ilegible "
    f"({type(exc).__name__})"
) from exc
```

And correct the comment at `store.py:419-420` to say what is true: *callers catch bare `Exception`; this net exists to convert an untyped escape into an operator-legible Spanish message, not to prevent a crash.* Given this batch's own standard on false records, the comment should not outlive the merge in its current form.

---

### F3 — The information-leak fix is incomplete: the same class reaches the same sink by an un-netted route  ·  **[LOW]**

*(This answers the operator's question 2 directly: **no, the fix is not complete** — though the gap is outside the diff's changed lines.)*

**What.** `_reindex`'s net was correctly changed to carry `type(exc).__name__` instead of the raw exception, precisely because `sqlite3`/`OSError` strings carry filesystem paths. But an `OSError` raised from `read_text` at `store.py:382-383` escapes un-netted (`F1`), and its `str` — full absolute path, including the OS username — is interpolated verbatim into the *same* operator-facing sinks.

**Where.** `mapper/store.py:382-383` → escapes → `mapper/app.py:454` and `mapper/app.py:1181`.

**Executed evidence.**

```
OPERATOR SEES:
[Errno 13] Permission denied: 'C:\\Users\\jjgh8\\AppData\\Local\\Temp\\leak2_fv_p8q2r\\m_nodos.yml'
contains user home dir name? True
```

**Why it matters.** Low absolute risk — a local single-user TUI showing the operator their own path is not a confidentiality breach. But it is measured against **the batch's own stated standard** (`Inc-1 review, F8`: these strings are shown to the operator, so do not put paths in them), and by that standard the class is still open via a different route.

**Recommendation.** Fixing `F1` as written above fixes this too — the suggested `except (OSError, UnicodeDecodeError)` arm emits `type(exc).__name__` and never the path. No separate work.

**The rest of the diff is clean on this axis.** I checked every message the diff adds or changes:

| Message | Interpolates | Path-bearing? |
|---|---|---|
| `no se pudo leer la ficha de {map_id}: {yml_path.name} ilegible` (`:400`, `:408`, `:430`) | `map_id` (caller-supplied), `Path.name` (basename) | **No** — `.name`, deliberately not the path |
| `no se pudo indexar {map_id}: {type(exc).__name__}` (`:442`) | type name only | **No** — this is the fix |
| `campo ilegible: {owner}.{key}` / `…[{i}]` (`:119`, `:129`) | internal owner labels + coerced `nid` | No |
| `documento duplicado: {doc.name!r} <- …` (`:301`) | sidecar values via `repr` | No |
| `nodo duplicado: {nid!r} <- {raw_nid!r}` (`:323`) | sidecar values via `repr` | No |
| `campo duplicado: {nid}.{ckey!r} <- {key!r}` (`:350`) | sidecar values via `repr` | No |

No new path-bearing interpolation is introduced anywhere in the diff.

---

### F4 — Warning amplification: a new, measured availability regression  ·  **[MEDIUM]**

*(The operator asked for judgement rather than a reflexive finding. My judgement: real, modest, and cheap enough to fix that I would take the fix.)*

**What.** `graph.load_warnings` is unbounded, `_mappings` appends one warning per malformed list entry, and `mapper/app.py:461` joins the **entire** list into a single `notify`.

**Where.** `mapper/store.py:129` (append site) → `mapper/model.py:98` (unbounded `list[str]`) → `mapper/app.py:461` and `mapper/app.py:1156` (whole-list join).

**Executed measurement.**

```
=== warning amplification (malformed attachment entries) ===
  n=   1000  sidecar=  0.00 MB -> warnings=   1000 joined=  0.04 MB  amp=17.67x    0.22s  peak=    0.6 MB
  n=  50000  sidecar=  0.10 MB -> warnings=  50000 joined=  1.89 MB  amp=18.88x    6.79s  peak=   31.7 MB
  n= 500000  sidecar=  1.00 MB -> warnings= 500000 joined= 19.39 MB  amp=19.39x   70.58s  peak=  308.5 MB
```

**A 1 MB file freezes the UI for 70 seconds** and allocates 308 MB, at roughly 19× amplification.

**This batch introduced it.** At `d877784` the identical input failed in O(1):

```
=== BASE d877784 behaviour on malformed attachments ===
  [scalar entry]  UNTYPED TypeError: 'int' object is not subscriptable
```

**Why it matters — and why it is not HIGH.** Against it: the amplification is new, it is superlinear in operator-visible latency, and the sala (`US-N13`) runs this **once per map in the workspace**, so a workspace of hostile maps multiplies it. For it: the input is a local file the operator controls, there is no confidentiality or integrity impact, no code execution, no data loss, and the process is killable. To be exposed, the operator must have obtained a hostile workspace (a shared or cloned map set) — plausible for this product, but not routine.

**Recommendation.** Cap the record list at the append site. ~5 lines, and it bounds the toast as a side effect:

```python
_MAX_WARNINGS = 50

def _warn(graph: Graph, msg: str) -> None:
    n = len(graph.load_warnings)
    if n < _MAX_WARNINGS:
        graph.load_warnings.append(msg)
    elif n == _MAX_WARNINGS:
        graph.load_warnings.append("… y más registros omitidos")
```

Route the seven `load_warnings.append` sites through it. Note this changes the record format that 18 existing test assertions pin, so it is a `software-dev` task with test updates, not a drive-by edit — which is why I recommend it rather than treating it as a merge blocker.

---

### F5 — The `_mappings` design rationale does not reproduce at the stated base  ·  **[LOW]**

**What.** `mapper/store.py:104-116` justifies the deliberate asymmetry (warn-and-continue for `attachments`; deny for `schema`/`documents`) on a measured behavioural difference:

> `preference: a malformed `attachments` entry used to be DISCARDED SILENTLY and`
> `the map still loaded, so the operator lost it with nothing anywhere saying so.`
> … `Measured (review Q1): schema/document item-scalars are denied typed; only`
> `attachments carried the silent-loss class.`

**Executed against `git show d877784:mapper/store.py`:**

```
=== BASE d877784 behaviour on malformed attachments ===
  [scalar entry]        UNTYPED TypeError: 'int' object is not subscriptable
  [str entry]           UNTYPED TypeError: string indices must be integers, not 'str'
  [null entry]          UNTYPED TypeError: 'NoneType' object is not subscriptable
  [list entry]          UNTYPED TypeError: list indices must be integers or slices, not str
  [dict missing kind]   UNTYPED KeyError: 'kind'
  [attachments non-list] UNTYPED TypeError: 'int' object is not iterable
  [valid]               LOADED  attachments=1 warnings=[]
```

**Nothing was silently discarded and the map did not load.** Every malformed attachment entry raised an *untyped* exception — the same outcome the comment attributes only to `schema`/`documents`. The observable asymmetry the comment calls "OBSERVABLE, not a preference" does not exist at `d877784`; all three families behaved identically.

**Why it matters.** The code is not thereby wrong — warn-and-continue for attachments is a defensible choice. But the recorded justification is false, in a batch whose own front matter states *"a map that lies is worse than a map that is merely stale."* And it is not inert: this is precisely the choice that creates `F4`, adopted on a measurement that does not hold.

**Recommendation.** Re-derive or withdraw the claim in the docstring. If warn-and-continue is a preference, record it as one — the choice survives being called a preference.

**By contrast, the batch's central measurement reproduces exactly**, and I want that on the record:

```
positions probed: 17   untyped escapes: 4
untyped by type: {'sqlite3.ProgrammingError': 3, 'builtins.TypeError': 1}
  att.kind / att.path / att.caption -> sqlite3.ProgrammingError
  doc.name                          -> builtins.TypeError
```

`P-1` (12 of 17 leak on `int` poison) and `P-3` (`ProgrammingError` ×3 + `TypeError` ×1) both hold. The 17-position census in `01-requirements.md:53-83` is sound, and the five positions it shows as already-clean are exactly the five the pre-existing `_coerce_field` covered.

---

### F6 — `docs/ARCHITECTURE.md`: two new "executed" citations are wrong, and a cross-module interface this batch widened is undocumented  ·  **[LOW]**

*(This answers the operator's question 7.)*

**First, the direct answer: nothing in the diff makes the security section false.** §1 *Context — the system boundary* (`docs/ARCHITECTURE.md:35`) was **not modified by this diff** — the changed tables are §2 *Composition* (`:64`) and §4 *Interfaces* (`:143`). §1 describes external actors (terminal, filesystem, `gh`, `git`, OS handlers) and the `osopen` crossing, none of which this diff touches. Verified that `store.py` gains no forbidden dependency:

```
$ git diff -U0 mapper/store.py | grep "^+" | grep "rich\|textual\|requests\|urllib\|socket\|http"
exit=1
```

The only import the 189-line diff adds is `from dataclasses import MISSING`. The §2 `store` row's Forbidden column ("Rendering, network, app lifecycle") holds.

**Two defects in claims the batch introduced as executed evidence:**

1. `search.py:7` is cited as the constructor. Line 7 is the `class SearchIndex:` statement; `__init__` is at `search.py:10`.
2. The doc quotes `grep -rn "SearchIndex" mapper/ tests/` as matching "only its own definition". Executed, it matches four lines — the extra source match is **this batch's own** `tests/test_repair_map_truth.py:116`. The *conclusion* (dead module, zero consumers) is independently TRUE and verified by AST walk; the quoted *proof* is not. Note the batch's own `D-R16` records exactly this hazard.

*Pre-existing, unrelated to this diff:* the §4 Canvas row writes `put(x,y,ch,tone)`; the real parameter is `style`.

**Structural gap — `Graph.load_warnings` is an undocumented cross-module interface, and this batch widened it.**

```
$ grep -n "load_warnings" docs/ARCHITECTURE.md
exit=1
```

Zero mentions anywhere in the map. Yet it is a producer/consumer contract: `store` writes it at 7 sites (**5 of them added by this diff** — `:119`, `:129`, `:301`, `:323`, `:350`), `app` reads it at 6 (`:459`, `:461`, `:1146`, `:1153`, `:1156`, `:1178`), and **18 test assertions pin its exact record format**. The §4 `Graph` row spells the shape as `nodes / edges / root_id / focus(...)` and omits three of `Graph`'s six fields.

Per the map's own rule — *"Changing one of these is trigger A3"* — an interface with no row can never fire that trigger. This batch changed that contract's record format five times and `F4`'s recommended fix would change it again.

**Recommendation.** Correct the two citations (`search.py:10`; restate the grep claim as the AST result, which is what actually proves it), and add a §4 row for `Graph.load_warnings` naming `store` as producer, `app` as consumer, and the record format as the frozen shape. That row is what makes `F4`'s cap a trigger-A3 decision instead of a silent format change.

---

### F7 — The top-level type refusal is a security control with no test that would notice its removal  ·  **[LOW]**

**What.** `store.py:404`'s `if not isinstance(sidecar, dict)` is an explicit, deliberately-added refusal — it is the guard I probed hardest in question 6, and it is the control that keeps a top-level list or scalar out of `.get`. Its own acceptance test cannot detect its deletion.

**Where.** `tests/test_repair_store_boundary.py:576`, `test_at_p03c_a_top_level_non_mapping_sidecar_is_refused`:

```python
with pytest.raises(MapStoreError):
    MapStore(tmp_path).load("m")
```

**Executed evidence (mutation).** Deleting the entire `if not isinstance(sidecar, dict)` block that this test's docstring names leaves **all 70 arms of the file green** — the generic `except Exception` net at `store.py:418` catches the resulting `AttributeError` and re-raises the same `MapStoreError`, so the assertion still passes. Its sibling `test_at_p03b:570` does assert `__cause__`; this one asserts neither message nor cause.

**Why it matters.** This is `F2`'s masking problem showing up in the test suite rather than at runtime: a broad net makes a specific control untestable, so the control can be removed silently. Low severity because the net genuinely does catch the case — deleting the guard degrades the diagnostic, it does not reopen a hole. But the batch's declared design has *two* independent controls here, and only one of them is pinned.

**Recommendation.** Tighten `test_at_p03c` to assert the guard fired rather than that *something* did — match `test_at_p03b`'s stricter form by asserting `exc.value.__cause__ is None` (the explicit refusal raises without `from`, where every net arm raises `from exc`). That single assertion distinguishes the two paths exactly.

---

## Categories checked and found clean

I want these on the record with what was actually run, so a later reader knows they were evaluated rather than skipped.

**Markup / ANSI injection into `load_warnings` (control C-17) — ARMED. No finding.**
This was the operator's largest concern, given the recorded prior incident of the same class. Traced `load_warnings` to **exactly two** render sites — `mapper/app.py:459-464` (sala) and `mapper/app.py:1146-1159` (`_notice_load_warnings`) — and both pass through `darkside.plain(...)` **and** `markup=False`. Tested with a real ESC / OSC-52 / unmatched-closing-tag payload delivered through a YAML double-quoted key (so the control bytes are genuine, not literal backslashes):

```
raw   : 'campo ilegible: \x1b[2J\x1b]52;c;cHduZWQ=\x07[bold].\x1b[31m[/bold]'
plain : 'campo ilegible: <FFFD>[2J<FFFD>]52;c;cHduZWQ=<FFFD>[bold].<FFFD>[31m[/bold]'
ESC(0x1b) survives plain? False | BEL? False | '[' ? True
Content.from_markup(joined) -> RAISES MarkupError: closing tag '[/bold]' does not match any open tag
Content(joined) [markup=False path]     -> renders literally
```

Reading this precisely: ESC and BEL are neutralised to U+FFFD by `_CONTROL_MAP` (`mapper/darkside.py:272-273`), so the OSC-52 clipboard write and the screen-clear are dead. `[` **does** survive `plain` by design — so **`markup=False` is the entire markup defense**, and it is present at both sinks. Confirmed by showing `Content.from_markup` *would* raise on the same string. There is also a standing AST class-guard, `tests/test_repair_fields.py:716` `test_tc_r38_every_interpolating_notify_passes_markup_false`, which enforces this as a class rather than sink-by-sink.

On the operator's specific worry about `repr()`: **`repr` is strictly safer than `str` here** — it escapes control characters itself, so the `f"key[{key!r}]"` / `nodo duplicado: {nid!r}` records cannot carry a live ESC even before `plain` runs.

**`yaml.safe_load` usage — clean.**
```
$ grep -rn "yaml\.\(safe_\)\?load\|yaml\.Loader\|FullLoader\|UnsafeLoader\|yaml\.load_all" --include=*.py .
./mapper/app.py:1536:  ... yaml.safe_load(data["yml"]) or {}
./mapper/diff.py:54:   sidecar = yaml.safe_load(yml_text) or {}
./mapper/store.py:385: sidecar = yaml.safe_load(yml_text) or {}
```
Three call sites, all `safe_load`. No `yaml.load`, no custom `Loader`, no `load_all`. A `!!python/object/apply:os.system` payload is refused: `ConstructorError` → typed `MapStoreError`.

**YAML bomb / aliases / merge keys — not a vector here. No finding.**
PyYAML shares alias *references* rather than expanding them, so billion-laughs does not materialise:
```
  levels=7 src=384 B  nominal_nodes= 4,782,969   0.09s  peak= 0.0 MB  -> OK warnings=1
```
A 384-byte file with 4.8 M nominal nodes parses in 0.09 s and ~0 MB. Recursive aliases, merge keys (`<<`), and aliased non-dict values were all tested and none gets past `isinstance(sidecar, dict)` (`store.py:404`) or the coercion ladder. The one real parser-level DoS is depth-based recursion, reported as `F1`.

**The type refusals — 24 hostile shapes, zero untyped escapes through `_graph_from_sidecar`.**
Top-level list/scalar/null; anchors, aliases, merge keys, recursive aliases; `!!binary`, bool/int/float/date/null keys; unhashable sequence keys; `!!python/*` tags; >4300-digit ints; `attachments`/`schema`/`documents`/`nodes` malformed as non-list, scalar-entry, missing-key, and non-dict. Every one resolved to either a load with recorded warnings or a typed `MapStoreError`. The coercion ladder and the `isinstance` refusals hold.

**The `_graph_from_sidecar` bypasses — checked, not a boundary.**
`mapper/app.py:1536` (`_pop_snapshot`) bypasses `load`'s guards, but its input is `yaml.safe_dump(self.store._build_sidecar(...))` — self-generated and already coerced, not attacker-shaped. `mapper/diff.py:59` bypasses them too but is wrapped in `except Exception: return None`. Neither is an untrusted-input crossing. (`diff.py:63`'s unguarded `store.load` is reported under `F1`.)

**The `osopen` crossing — improved, not weakened. No finding.**
The operator flagged `osopen` as the system's highest-risk crossing and the store as where its text originates, so I checked whether the coercion changes what reaches it. It does, favourably: `Attachment.kind` and `Attachment.path` are now guaranteed `str` at the boundary, where at `d877784` they were raw. Critically, **`osopen` does not depend on that guarantee** — it re-validates independently at `mapper/osopen.py:73` (`if not isinstance(target, str) or not target.strip()`) and rejects C0/C1 controls at `:81`, so the store's coercion is an added layer rather than the only one. Defense-in-depth is intact, and the store still imports nothing from `osopen` (§3 ban holds).

One **behaviour change** worth recording, which the batch does not mention. A sidecar with `path: 12345` (a YAML int) was refused at base with `REFUSED_TYPE` because `isinstance(target, str)` failed. It now coerces to `"12345"`, passes the type gate, and — if `<workspace>/12345` exists as a file — launches. **This grants no new capability:** the same sidecar author could always have written `path: "12345"` as a string and obtained exactly that result at base, and the confinement (`:120`), existence and not-a-directory (`:121`) checks all still run ahead of the launcher. So it is a change in which *malformed* inputs reach the guard, not a change in what the guard permits. Recording it because it is a live behaviour change at the crossing the map calls highest-risk, and it belongs in the batch's record rather than being discovered later.

**Secrets and credentials — clean.**
No API key, token, password, private key, or `.env` content in the diff, the four new test files, or the `.dev-flow` artifacts. `git ls-files | grep -iE "\.env|credential|secret|\.pem|\.key|id_rsa"` → empty. `.gitignore` explicitly covers `.env`, `.env.*`, `*.db`, `mapper.db`, `.mapper/`, and `scratch/`. The batch artifacts' "Token" references are lexical parser tokens, not credentials.

**Dependencies / supply chain — no change.**
`pyproject.toml` is untouched. The diff adds exactly one import, stdlib `dataclasses.MISSING`. No new package, no lockfile change, no install script, no typo-squat surface.

**External tool / integration surface — none.**
This batch adds no MCP server, no Composio connector, no n8n node, no third-party API, no network call, no subprocess, and no new outbound action. `osopen` — the system's highest-risk crossing — is not touched. Nothing to scope-review.

**Destructive command surface — none.**
No `rm -rf`, no `Remove-Item -Recurse`, no force push, no `DROP TABLE`, no schema migration, no mass update. `_reindex`'s `DELETE` statements are scoped by `map_id` and unchanged by this diff. The SQLite index is declared rebuildable and text remains the source of truth.

**Auth / deploy — not applicable.**
No auth flow, token storage, session, or multi-tenant boundary exists in this codebase. No deploy surface in this batch.

**Client-data / LFPDPPP exposure — none.**
Nothing in this batch causes client data to leave the local system. The only egress-shaped concern was the path-in-message class, reported as `F3`, and it renders locally to the operator only.

---

## Not verified / open

Stated plainly so a later reader does not mistake absence for clearance.

1. ~~Acceptance-test rigour of the four new test files.~~ **Completed — see the addendum.** It was mutation-tested, and produced one security-relevant result promoted to `F7`. The standing implication holds either way: **the suite is fully green (517 passed, 0 failed) while `LLR-STO.1.1` threshold 3 is unmet** (`F1`), so the tests do not assert threshold 3 as written.
2. **`_reindex`'s SQLite behaviour under a hostile-but-coerced graph** was exercised only through `load`. I did not fuzz `_reindex` directly, so I cannot speak to its behaviour if a future caller reaches it with an uncoerced `Graph`.
3. **Concurrency** — two `mapper` processes over one workspace, or a file mutated between `load` and `_reindex` — was out of scope and not tested. `_atomic_write` (`store.py:447`) suggests the author considered it on the write side.
4. **`.mapper/state.json`** (`store.py:522-531`) is locally generated, so I treated it as trusted and only noted its missing `UnicodeDecodeError` arm under `F1`. If that file is ever synced or shared, it becomes an untrusted-input boundary and needs its own pass.

---

## Answers to the seven questions asked

| # | Question | Answer |
|---|---|---|
| 1 | Are the two `except Exception` nets a safe failure mode? | **Partly, and the recorded justification is false.** Ordering (`except MapStoreError: raise` before `except Exception`) and `raise … from exc` are both correct and verified. But no caller catches `MapStoreError` (zero hits), so the nets do not prevent any crash that would otherwise happen; and with zero logging the masked type is unrecoverable. **I do not accept the prior reviewer's trade as recorded.** → `F2` |
| 2 | Is the information-leak fix complete? | **No.** The `_reindex` fix is correct, but `OSError` from `read_text` escapes un-netted and delivers a full absolute path (with username) to the same sink. No *other* message in the diff splices path-bearing content. → `F3` |
| 3 | Does `repr()` interpolation reach a markup-parsing sink? | **No.** Two sinks, both `darkside.plain` + `markup=False`, plus a standing AST class-guard. ESC/BEL neutralised; `markup=False` verified as the real markup defense. `repr` is safer than `str` here. **C-17 armed.** |
| 4 | Is `load_warnings` bounded — real DoS or acceptable? | **Unbounded, and this batch introduced the amplification.** Measured 19× / 70 s / 308 MB from a 1 MB file, vs O(1) failure at base. My judgement: real but modest — MEDIUM, worth the ~5-line cap, not worth blocking. → `F4` |
| 5 | Is `safe_load` used everywhere? | **Yes.** Three call sites, all `safe_load`. No `yaml.load`, no custom loader. Clean. |
| 6 | Can crafted YAML get past the type refusals? | **No.** 24 hostile shapes including anchors, recursive aliases, merge keys, `!!python/*`, and a 4.8 M-node alias bomb — zero escapes through `_graph_from_sidecar`. The only parser-level vector is recursion depth, which is `F1`, not a refusal bypass. |
| 7 | Does the diff make anything in the map false? | **Not in the security section** — §1 is unmodified and the `store`/`osopen` rows still hold. Two new "executed" citations in §2/§4 are wrong, and `Graph.load_warnings` is an undocumented cross-module interface this batch widened five times. → `F6` |

---

## Verdict

- [x] **OK to ship** — no HIGH finding. **CLEARED TO MERGE.**
- [ ] OK to ship with the listed mitigations applied first
- [ ] Block — must fix HIGH findings before ship

**Plainly: this branch is CLEARED TO MERGE.** No finding reaches HIGH. Nothing here leaks a secret, opens a permission, reaches the network, or performs a destructive or irreversible action, and the batch measurably hardens the boundary it set out to harden.

**Two recommendations, in priority order.**

1. **Fold `F1` in before merge.** It is ~6 lines, it closes `F3` at the same time, and it is the difference between `LLR-STO.1.1` threshold 3 being *met* and being *asserted*. Merging with a declared acceptance threshold unmet is a gate-integrity cost that is cheaper to pay now than to carry.
2. **`F2`'s comment correction before merge; `F2`'s diagnostic and `F4`'s cap as a follow-up batch.** The false premise at `store.py:419-420` should not outlive the merge — this batch's own standard forbids it, and it is a comment edit. The `type(exc).__name__` addition and the `load_warnings` cap both change a record format that 18 tests pin, so they want their own increment with test updates, plus the `F6` §4 row so the format change fires trigger A3 properly.

`F5`, `F6` and `F7` are LOW and can ride the same follow-up. `F7` is a one-line test change (`assert exc.value.__cause__ is None`, verified to distinguish the guard from every net arm) and is worth taking with `F1` since both touch the same nets.

---

## Evidence checklist

| Item | | Evidence |
|---|---|---|
| Each finding has what · where · why · recommendation | ✓ | `F1`–`F6` above, each with `file:line` |
| Each finding has a severity rating | ✓ | 3 MEDIUM (`F1`, `F2`, `F4`), 4 LOW (`F3`, `F5`, `F6`, `F7`); no HIGH |
| No secret values appear in this output | ✓ | Sweep found none to report; no credential material exists in the batch |
| Verdict is explicit | ✓ | **CLEARED TO MERGE**, no HIGH |
| New tool/integration scope + blast radius addressed | ✓ | **N/A and stated** — this batch adds no MCP/Composio/n8n/third-party/network/subprocess surface; `pyproject.toml` untouched; one stdlib import added |
| Injection control C-17 traced to every render site | ✓ | Two sinks (`app.py:461`, `app.py:1156`), both `plain` + `markup=False`, verified with a live ESC/OSC-52/markup payload |
| Base-commit claims independently re-measured | ✓ | `git show d877784:mapper/store.py` into scratch; census reproduces (`ProgrammingError`×3 + `TypeError`×1); `_mappings` rationale does not (`F5`) |
| No repo file edited, no git mutation run | ✓ | Only this file written; all experiments in scratch |
| Acceptance evidence independently mutation-tested | ✓ | Addendum below; 517 passed / 17 slow passed; one result promoted to `F7` |

---

## Addendum — acceptance-evidence audit (delegated, mutation-tested)

Run independently on a scratch copy of the tree; the repo was not mutated.

**Suite is fully green.** `PYTHONUTF8=1 python -m pytest tests/ -q` → **517 passed, 17 deselected, 0 failed, 0 errors, 0 skipped** (159.5 s). Slow lane `-m slow` → **17 passed** (38.6 s). The four new files contribute **104 of 517** fast-lane tests and 1 of 17 slow. Only pre-existing noise (an asyncio fixture-scope deprecation and four Textual timer teardown lines).

**`test_repair_store_boundary.py` — genuinely rigorous. This is the file carrying the security repair, and it survives mutation.** Degrading the refusal record reddens 17 arms; silently dropping a malformed `_mappings` entry reddens 2; hard-coding `""` instead of the dataclass default reddens 2; removing the outer sidecar-walk net reddens 5; removing the `_reindex` net reddens 1. `_EXPECTED_REFUSAL` is hard-coded and compared against a **list**, so `in` is exact element equality, not substring — the format is genuinely pinned. Every loop that could iterate zero times is fenced (`:244`, `:422`, and a `>= 17` floor at `:219`). Two soft spots: `test_at_p03c:576` (→ `F7`), and `_text_field_names:71-88` sharing the `f.type in ("str", str)` predicate with the implementation, so retyping `Ficha.title` to `Any` would blind test and code in lockstep — backstopped, not closed, by the `>= 17` floor.

**`test_repair_map_truth.py` — overstates itself. Three verified green mutants.** This is the file that guards the doc-truth property, and it reinforces `F6` rather than covering it:
- `test_at_p04:86` checks path **existence only**, never ownership or coverage. Re-attributing the `store` row's owned paths to `mapper/model.py` (wrong owner, real file) → **26 passed**. Adding an unmapped `mapper/newmod/thing.py` to the tree → **26 passed**. So neither the staleness rule nor the exclusive-ownership rule the doc says the A-family triggers consume is tested at all.
- `test_at_p05:121` is a verbatim-substring pin. Re-wording the same lie (a paraphrased "`load` returns a tuple … `reindex()` is public") → **26 passed**. It catches the exact old sentence and no paraphrase, and no *new* falsehood.
- `test_at_p05b:145` has its entire body inside `if "mapper/views/state.py" in text:`. Paraphrasing the path mention *and* flipping the marker to `PRESENT AND SHIPPED` → **26 passed**, a silent no-op reporting green.

**`test_repair_golden_census.py` — one tautological arm.** `test_tc_p06:61` derives its oracle from the artifact under test (`_renderers()` is `sorted({k[0] for k in _census()})`), so deleting all four `OutlineRenderer` pins leaves it **green** — the exact "a pin being removed" regression its docstring claims to catch. The mutant *is* caught, but only by `test_tc_p06b:89` and `test_tc_p06c:122`, the two literal pins the file's own prose disparages: net coverage is fine, the stated rationale is inverted. Separately, `test_at_p07:132` substring-matches prose the batch itself authored in `.dev-flow/state.json`, which is **unmodified on this branch** — it passes by construction and can catch no regression in `load` or in the pins.

**`test_repair_perf_shape.py` — honest, but thin.** There is **no timing threshold at all**, so nothing is flaky and nothing timing-related can fail; the file says so openly and gives a defensible reason. Two notes: its declared "record the cost" output is a bare `print` at `:92` that pytest's capture swallows in both lanes, so the measurement exists only in source; and `test_tc_p08:62` asserts the closed form of the loop the same file wrote from the same constants — it tests the fixture, not the product, and the slow arm's only product assertion is `assert text.plain.strip()`, which a renderer emitting garbage would pass.

**Security bearing.** Only `test_at_p03c` rises to a finding (`F7`) — it is the one case where a *security control* is unpinned. The `map_truth` and `golden_census` weaknesses are evidence-integrity issues in the same family as `F5`/`F6`: they mean the doc-truth guarantees this batch advertises are narrower than stated. None of them weakens the store repair, whose own test file is the strongest of the four.
