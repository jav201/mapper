# 01b — Acceptance Design (black-box gates)

Batch `2026-08-25-ui-next-batch-01` · repo `mapper` · variant A «taller»
Author: `qa-reviewer` · Phase 1 · Artifact language: English · Product UI strings: Spanish

---

## 1. BLUF

This suite gates five stories on **observable behaviour through the shipped TUI surface**, not on the
service objects underneath. Every `AT-NNN` below drives real `pilot.press(...)` keystrokes against the
real screen, and reads its oracle either from a widget the operator can actually see or from the
`.mmd` / `_nodos.yml` text files re-loaded through the **unmodified** `MapStore.load`. The existing
suite is blind in five specific, *measured* ways, and each one is a defect that ships today:

| # | Blind spot | Measured evidence |
|---|---|---|
| 1 | **The palette dispatches nothing.** Zero of 33 `KEYMAP` entries resolve to an `action_*` method, because `KeyBinding.action` holds a Spanish LABEL (`"agregar hijo"`), while `MapperApp.action_palette` does `getattr(screen, "action_" + action.replace(" ", "_"))` — `action_agregar_hijo` does not exist. | `mapper/keymap.py:18-59`, `mapper/app.py:1672-1684`; probe output `DISPATCHABLE on MapScreen+App: 0` of `KEYMAP size: 33` |
| 2 | **The only test that claimed to cover it is vacuous** — it passes *because* nothing dispatched. See §3. | `tests/test_palette.py:17-46` |
| 3 | **`x` destroys a subtree with no confirmation and no recovery.** Pressing `x` on non-root `a` (which had child `a1`) removed both, silently, staying on `MapScreen`. | `mapper/app.py:1520-1526` (`do_archive(True)`); probe: `on-disk nodes after x: ['b','c','root']`, `screen after x: MapScreen` |
| 4 | **Undo does not survive leaving the map.** `self._snapshots` is per-screen state. Depth `1` before `q`, depth `0` on re-entry; `u` afterwards is a no-op and the deleted subtree is unrecoverable. | `mapper/app.py:1094`, `1293-1318`; probe: `new screen snapshots depth: 0`, `nodes after undo on re-entry: ['b','c','root']` |
| 5 | **File-derived text is rendered wrong in both directions.** `rich.markup.escape` is applied inside `Text.append(...)` paths, where markup is *not* parsed — so the backslash leaks to the screen. And nothing strips ANSI, which passes through into the rendered `Content`. | `mapper/app.py:1258,1261,1272-1289`; probe: rendered plain = `'▸ \\[bold red]PWN\\[/] \x1b[31mX\x1b[0m [unclosed…'` — `has backslash-bracket: True`, `has ESC: True` |

Nineteen acceptance tests follow: `AT-N01a`–`AT-N01e`, `AT-N02a`–`AT-N02d`, `AT-N03a`–`AT-N03d`,
`AT-N04a`–`AT-N04b`, `AT-N05a`–`AT-N05e`. Each maps to **exactly one** on-disk test function driving
the whole chain end to end (C-18) — no requirement is "covered in parts".

> **One story is not fully testable as written.** US-N02's promise that "Open hands the attachment to
> the OS default application" has no black-box oracle: verifying that a real OS application launched
> would mean launching one. §2.2 states the seam the implementation must expose so the *reachable*
> part is gated, and states plainly which part is not gated. I did not invent an oracle for it.

### 1.1 Precondition on US-N03 that the implementation must satisfy first

`KeyBinding` today conflates three things into two fields, and the ATs below cannot be written until
that is split. Measured drift between `KEYMAP` and `MapScreen.BINDINGS`:

- `KEYMAP` keys absent from `BINDINGS`: `/ · c · ctrl+s · esc · i · n · p · t · tab · v · ↵` (11)
- `BINDINGS` keys absent from `KEYMAP`: `enter · escape · slash` (3)

The last three are the same three physical keys as `↵ · esc · /` — `KEYMAP.key` holds a **display
glyph**, `BINDINGS` holds a **Textual key name**. So `KeyBinding` must carry, at minimum:

```python
KeyBinding(key="enter", glyph="↵", action="open_ficha", label="abrir", group="nav")
#           ^Textual     ^display   ^method name       ^Spanish UI
```

`key` is what `BINDINGS` and `pilot.press` use; `glyph` + `label` are what the keybar, palette and
help display; `action` is the bare method-name suffix. Every AT in §2.3 asserts against these fields.

---

## 2. Per-story acceptance tests

Notation: `press(k)` is `await pilot.press(k)`; `store` is the app's own `MapStore`; "re-read from
disk" always means a **fresh** `MapStore(workspace).load(map_id)`, never the in-memory `screen.graph`.

---

### 2.1 US-N01 — edición in-situ

Shipped surface: the right-hand **inspector panel** on `MapScreen` (new; widget id `#inspector`),
reached and driven by keystrokes. Target test file: **`tests/test_inspector.py`**.

Fixture `legacy` used by all five (deliberately **non-default** throughout — C-10):

```python
schema = [
    SchemaField("D", "documento",   required=True),
    SchemaField("O", "dueño",       required=True),
    SchemaField("E", "estado",      required=True),
    SchemaField("C", "criticidad",  required=False),
]
root  = Node("root", Ficha(title="Raíz", state="ok"))
audit = Node("audit", Ficha(title="Auditoría", state="risk",
                            fields={"D": "acta-2024", "C": "media"}))   # O and E MISSING
```

Note the shape: `D` (the *first* schema field) is **filled** and `O` is the first *missing* one. Any
implementation that focuses `schema[0]` instead of the first missing field is red on AT-N04a.

---

#### AT-N01a — a title edited in the inspector survives a full disk round-trip

- **Observable outcome:** the operator types a new title into the inspector; the `.mmd`/`_nodos.yml`
  on disk carry that exact string, and reloading the map shows it.
- **Surface:** `MapScreen` → `#inspector` → `#insp-title` Input.
- **Pilot chain:**
  ```python
  app.push_screen(MapScreen("legacy")); await pilot.pause()
  await pilot.press("l")             # nav to 'audit'  (real key, not nav.cursor = ...)
  await pilot.press("i")             # open/enter inspector
  await pilot.press("tab")           # focus lands on the title field
  for _ in range(len("Auditoría")):
      await pilot.press("backspace")
  await pilot.press(*"Auditoria Legacy 2026")
  await pilot.press("ctrl+s")        # guardar
  await pilot.pause()
  ```
- **Oracle (C-12, output-then-consume):**
  ```python
  reloaded = MapStore(app.store.workspace).load("legacy")     # unmodified loader
  assert reloaded.nodes["audit"].ficha.title == "Auditoria Legacy 2026"
  assert "Auditoria Legacy 2026" in (ws / "legacy_nodos.yml").read_text(encoding="utf-8")
  assert not list(ws.glob("*.tmp"))                            # atomic write left no residue
  ```
  Asserting the **exact string**, never `!= ""` (C-10).
- **RED mutation:** in the inspector's save handler, drop the `self.store.save(self.map_id, self.graph)`
  call (keep the in-memory assignment). → the `reloaded.…title` arm goes red with the old title
  `"Auditoría"`; the `.yml` substring arm goes red too. A second, sharper mutation: change
  `MapStore._atomic_write` to `tmp.write_text(...)` without `tmp.replace(path)` → the `*.tmp` arm goes red.
- **Controls:** C-10, C-12, C-16, C-18.

---

#### AT-N01b — every state branch is reachable and persists (one AT, four parametrized arms)

- **Observable outcome:** each of `ok / risk / late / blocked` can be set from the inspector and each
  lands on disk as that exact token.
- **Surface:** `#insp-state` (a cycling field or `Select`); driven by real keys.
- **Pilot chain:** parametrized over `STATES = ("ok", "risk", "late", "blocked")` **imported from the
  implementation module**, not hand-listed in the test:
  ```python
  @pytest.mark.parametrize("target", STATES)
  ...
  await pilot.press("l", "i")
  await pilot.press("tab", "tab")        # focus the state field
  while inspector.state_value != target: # real key traversal, bounded
      await pilot.press("right")
      assert loops < len(STATES) + 1
  await pilot.press("ctrl+s")
  ```
- **Oracle:** `MapStore(ws).load("legacy").nodes["audit"].ficha.state == target`, **and** the visible
  inspector line contains the Spanish label for that state — `inspector.query_one("#insp-state").render().plain`
  contains `target`.
- **RED mutation:** make the state setter clamp to `"ok"` (`state = target if target == "ok" else "ok"`).
  → the three non-`ok` arms go red; the `ok` arm stays green, which is exactly why one AT per policy
  branch is required (C-10).
- **Controls:** C-10, C-12, C-16, C-18.

---

#### AT-N01c — schema fields are shown by `SchemaField.label`, never by the raw key letter

- **Observable outcome:** the inspector row for field `O` reads `dueño`, and the letter `O` is not
  presented to the operator as the field's name.
- **Why this AT exists:** today `_ficha_text` hardcodes three key letters to three hardcoded Spanish
  words (`mapper/app.py:1270-1277` — `"documento"` for `D`, `"dueño"` for `O`, `"creado"` for `Y`) and
  `_FichaScreen` prints the **raw key** for everything else (`mapper/app.py:252`:
  `text.append(f"  {escape(key)} ", …)`). Neither reads `SchemaField.label`. A map whose schema
  renames `O` to `"responsable"` still shows `dueño`.
- **Pilot chain:** the fixture schema is mutated for this AT so labels are *non-default* and cannot
  coincide with the hardcoded strings:
  ```python
  schema = [SchemaField("D", "acta formal", required=True),
            SchemaField("O", "responsable", required=True), ...]
  await pilot.press("l", "i"); await pilot.pause()
  rendered = app.screen.query_one("#inspector").render().plain
  ```
- **Oracle:**
  ```python
  assert "acta formal" in rendered and "responsable" in rendered
  assert "documento" not in rendered and "dueño" not in rendered   # hardcoded labels are gone
  assert not re.search(r"(?m)^\s*[DOEC]\s{2,}", rendered)          # no bare key letter as a row name
  ```
- **RED mutation:** revert the inspector row builder to `field.key` instead of `field.label`. → the
  first arm goes red (`"responsable"` absent). Complementary mutation: leave the `mapper/app.py:1270-1277`
  hardcoded block in the inspector → the second arm goes red.
- **Controls:** C-10, C-16, C-18.

---

#### AT-N01d — a required field cleared back to empty is flagged, and the flag clears when refilled

- **Observable outcome:** emptying `D` (which was filled) makes the inspector mark that row as
  required-and-missing and drops the coverage meter by one; refilling it restores both.
- **Pilot chain:**
  ```python
  await pilot.press("l", "i", "tab")          # focus the D field (already 'acta-2024')
  for _ in range(len("acta-2024")):
      await pilot.press("backspace")
  await pilot.press("ctrl+s"); await pilot.pause()
  after_clear = app.screen.query_one("#inspector").render()
  await pilot.press(*"acta-2025"); await pilot.press("ctrl+s"); await pilot.pause()
  after_refill = app.screen.query_one("#inspector").render()
  ```
- **Oracle** — assert on *content*, both directions:
  ```python
  MISSING = "requerido"                       # the Spanish flag string
  assert after_clear.plain.count(MISSING) == 3      # D, O, E  -- exact count, not >0
  assert MISSING not in row_for(after_refill, "acta formal")
  assert after_refill.plain.count(MISSING) == 2     # O, E
  reloaded = MapStore(ws).load("legacy")
  assert reloaded.nodes["audit"].ficha.required_coverage(reloaded.schema) == (1, 3)
  ```
- **RED mutation:** change the flag predicate from `f.required and not ficha.fields.get(f.key)` to
  `f.required and f.key not in ficha.fields` (a very plausible slip). → the `count == 3` arm goes red
  with `2`, because `D` is present-but-empty-string and would no longer be flagged.
- **Controls:** C-10, C-12, C-16, C-18.

---

#### AT-N01e — hostile file-derived text renders literally (security lens)

- **Observable outcome:** a ficha whose title, notes, a field value and an attachment caption all
  contain Rich markup, ANSI escapes and unbalanced brackets renders those characters **as characters**
  — no markup parse, no style leak, no stray backslash, no crash.
- **Threat model:** `_nodos.yml` is a plain text file the operator or a teammate edits by hand, and
  `import_csv` writes into it. It is untrusted input to a Rich render path.
- **What I measured on today's code** (probe through a real pilot on `#map-ficha`):
  ```
  PLAIN: '▸ \\[bold red]PWN\\[/] \x1b[31mX\x1b[0m [unclosed   ▱\n …'
  has backslash-bracket: True     has ESC: True
  ```
  Both are defects, and they pull in **opposite** directions:
  - `mapper/app.py:1258` does `text.append(escape(ficha.title), style=…)`. `Text.append` and
    `Text.assemble` **do not parse markup**, so `escape()` here is not a defence — it *injects* a
    visible backslash. Verified: `Text.assemble((escape(h), s)).plain` → `'\\[bold]…'`;
    `Text.assemble((h, s)).plain` → `'[bold]…'` with a single span carrying only the caller's style.
  - Neither path touches ANSI. `\x1b[31m` survived into the rendered `Content` and reaches the terminal.

  Meanwhile the *opposite* sink is real: `Static("[bold red]PWN[/]")` **does** parse markup — measured
  `plain='PWN'`, `spans=[Span(0,3,'bold red')]`. So `escape()` is correct there and only there.
  `mapper/screens/coverage.py:85` passes a bare `escape(...)` **str** into `DataTable.add_row`, which
  stores it as a `str` — that one is right for the same reason.

- **Prescribed construction — the inspector MUST use exactly this, and nothing else:**
  ```python
  # mapper/darkside.py
  _CTRL = {c: None for c in range(0x20) if c not in (0x0A,)} | {c: None for c in range(0x7F, 0xA0)}

  def plain(s: str) -> str:
      """Neutralize file-derived text for a Text.* path: strip C0/C1 controls, keep newline.

      Does NOT call rich.markup.escape -- Text.append/Text.assemble do not parse markup,
      so escaping there leaks a literal backslash to the screen.
      """
      return (s or "").translate(_CTRL)
  ```
  and every value goes in as `text.append(darkside.plain(value), style=…)` /
  `Text.assemble((darkside.plain(value), style))`. The inspector must **never** hand a bare `str` to
  `Static(...)`; it always builds a `Text`. `rich.markup.escape` must not appear in the inspector at all.
- **Pilot chain:**
  ```python
  H = "[bold red]PWN[/] \x1b[31mX\x1b[0m [unclosed"
  ficha = Ficha(title=H, notes=H, fields={"D": H},
                attachments=[Attachment("file", "c:/tmp/x.pdf", caption=H)])
  # ... save via store, then:
  await pilot.press("l", "i"); await pilot.pause()
  content = app.screen.query_one("#inspector").render()
  ```
- **Oracle (four arms):**
  ```python
  p = content.plain
  assert "[bold red]PWN[/]" in p          # markup survives as literal characters
  assert "[unclosed" in p                 # unbalanced bracket does not eat the rest
  assert "\\[" not in p                   # no over-escape artifact
  assert "\x1b" not in p and not any(ord(c) < 0x20 and c != "\n" for c in p)
  assert all(sp.style in ALLOWED_STYLES for sp in content.spans)   # no style leaked from payload
  ```
  `ALLOWED_STYLES` is derived from the darkside palette constants at runtime, not hand-listed.
- **RED mutation:** two, each reddening a different arm. (a) Build one inspector row with
  `Static(f"[dim]{value}[/]")` instead of a `Text` → `"[bold red]PWN[/]" in p` goes red (the payload
  was parsed) and the `ALLOWED_STYLES` arm goes red (a `bold red` span appears). (b) Re-introduce
  `rich.markup.escape` in the `Text.append` path → the `"\\[" not in p` arm goes red. (c) Drop the
  `translate(_CTRL)` → the `"\x1b" not in p` arm goes red.
- **Controls:** C-17, C-10, C-16, C-18.

---

### 2.2 US-N02 — adjuntos

Shipped surface: the inspector's **attachment list** (`#insp-attachments`). Target test file:
**`tests/test_attachments.py`**.

> **Testability limit, stated plainly.** "Hands the attachment to the OS default application" cannot be
> asserted black-box — the only honest end-to-end oracle would be a real application launching, which a
> test must not do. What **is** gateable is that the handler resolves the attachment to the right target
> and calls the single opener with it. This requires the implementation to expose one seam:
> ```python
> # mapper/open_external.py
> def open_external(target: str, kind: str) -> None: ...   # url -> webbrowser.open, file -> os.startfile / xdg-open
> ```
> AT-N02b monkeypatches **only** `open_external`; the entire path from keypress → inspector → attachment
> resolution → call is real. The last hop (opener → OS) is **UNGATED** and must be signed off by manual
> inspection — logged as `MAN-01` in §5. Do not let a green AT-N02b be read as "opening works".
> There is no `os.startfile` / `webbrowser` / `xdg-open` call anywhere in `mapper/` today
> (grep: zero hits outside `diff.py` and `github.py`, both git subprocess calls), so this is greenfield.

#### AT-N02a — an attachment added in the inspector round-trips through disk

- **Observable outcome:** the operator adds a `url` attachment with a caption; it appears in the list
  and is present in `_nodos.yml` with that exact kind/path/caption.
- **Pilot chain:**
  ```python
  await pilot.press("l", "i")
  await pilot.press("A")                    # 'agregar adjunto' opens the prompt
  await pilot.press(*"https://ejemplo.mx/acta.pdf"); await pilot.press("enter")
  await pilot.press(*"acta firmada");        await pilot.press("enter")
  await pilot.press("ctrl+s"); await pilot.pause()
  ```
- **Oracle:**
  ```python
  atts = MapStore(ws).load("legacy").nodes["audit"].ficha.attachments
  assert [(a.kind, a.path, a.caption) for a in atts] == [
      ("url", "https://ejemplo.mx/acta.pdf", "acta firmada")]
  assert "acta firmada" in app.screen.query_one("#insp-attachments").render().plain
  ```
  Exact tuple equality, including the inferred `kind` (C-10 — a `kind` hardwired to `"file"` fails here).
- **RED mutation:** hardwire the kind inference to `"file"`. → the tuple-equality arm goes red on the
  `kind` element while path and caption still match.
- **Controls:** C-10, C-12, C-16, C-18.

#### AT-N02b — open dispatches the right target for both kinds (two parametrized arms)

- **Observable outcome:** pressing `enter` on a `url` row hands the URL to the opener; on a `file` row
  it hands the resolved absolute path.
- **Pilot chain:** fixture node carries **both** a url and a file attachment, in that order.
  ```python
  calls = []
  monkeypatch.setattr("mapper.inspector.open_external",
                      lambda target, kind: calls.append((target, kind)))
  await pilot.press("l", "i")
  await pilot.press("A")            # focus the attachment list
  await pilot.press("down" * idx)   # real traversal to the row under test
  await pilot.press("enter")
  ```
- **Oracle:** `assert calls == [(expected_target, expected_kind)]` — for the file arm,
  `expected_target == str((ws / "docs/acta.pdf").resolve())`, i.e. the *resolved* path, not the stored
  relative one.
- **RED mutation:** make the handler always pass `attachment.path` verbatim. → the `file` arm goes red
  (relative path, not resolved); the `url` arm stays green — which is why both arms are required.
- **Controls:** C-10, C-16, C-18.

#### AT-N02c — a removed attachment is gone from disk, and only that one

- **Pilot chain:** node starts with **three** attachments; traverse to the middle one with real `down`
  presses, press `D`, confirm, `ctrl+s`.
- **Oracle:** `[a.path for a in reloaded…attachments] == [first.path, third.path]` — exact remaining
  list, in order. Not `len(...) == 2`.
- **RED mutation:** change the removal to `attachments.pop()` (drop the last). → red: the list comes
  back `[first, second]`.
- **Controls:** C-10, C-12, C-16, C-18.

#### AT-N02d — opening a file attachment whose path does not exist warns and does not call the opener

- **Observable outcome:** an operator-visible Spanish error; the opener is never invoked.
- **Pilot chain:** attachment `("file", "docs/no-existe.pdf")`; same traversal as AT-N02b; `enter`.
- **Oracle:**
  ```python
  assert calls == []                                       # opener NOT called
  assert "no existe" in app.screen.query_one("#map-toast").render().plain
  ```
- **RED mutation:** remove the `Path(...).exists()` guard. → the `calls == []` arm goes red.
  Note the `url` kind must be *exempt* from the existence check — a second arm asserts a `url`
  attachment still opens, so an over-broad guard is also caught.
- **Controls:** C-10, C-16, C-18 (error-state coverage).

---

### 2.3 US-N03 — keymap único

Target test file: **`tests/test_keymap_conformance.py`** (replaces
`tests/test_palette.py::test_palette_dispatches_selected_action`, which is deleted — see §3).

#### AT-N03a — universal: every keymap entry offered on this screen actually dispatches

- **Observable outcome:** for **every** `KeyBinding` in the groups the map screen exposes, selecting it
  in the palette with real keys invokes that binding's `action_*` method.
- **Where the set comes from (C-31/C-40):** `[b for b in KEYMAP if b.group in MapScreen.KEY_GROUPS]`,
  computed at **import time from the live module** — nothing is hand-listed. Guarded by
  `test_keymap_completeness_guard` (`len(KEYMAP) >= 33`, all seven group names present, no blank
  fields) and by a collection-time `assert MAP_SCREEN_BINDINGS`, so an emptied or shrunken keymap
  fails loudly instead of making the parametrized universal vacuously green.
- **What is certified, precisely:** *resolvability and dispatch of the selected entry*. It does **not**
  certify each action's semantics — those belong to the per-story ATs. Saying otherwise would be the
  same over-claim that made the old test vacuous.
- **Full code in §3.**
- **RED mutation:** revert any single `KeyBinding.action` to a Spanish label (e.g. `"open_ficha"` →
  `"abrir"`). → exactly that one parametrized arm goes red with
  `no action_abrir on MapScreen or MapperApp`; the other 19 stay green, so the failure names the
  offending entry. Second mutation: make `CommandPalette.action_run_selected` dismiss `None` whenever
  the list is non-empty → **all** arms go red (this is the mutation the old test could not detect).
- **Controls:** C-31, C-40, C-16, C-18.

#### AT-N03b — screen `BINDINGS` are generated from `KEYMAP`, in both directions

- **Observable outcome:** no key works that the keymap does not list, and no key the keymap lists for
  this screen fails to be bound.
- **Oracle** (set equality, both directions — today it fails 11 one way and 3 the other):
  ```python
  bound   = {b.key if isinstance(b, tuple) else b.key for b in MapScreen.BINDINGS}
  claimed = {b.key for b in KEYMAP if b.group in MapScreen.KEY_GROUPS}
  assert bound == claimed, f"missing={claimed - bound} extra={bound - claimed}"
  assert all(b.key not in DISPLAY_GLYPHS for b in KEYMAP)   # 'enter', never '↵', in .key
  ```
- **RED mutation:** append a hand-written `("z", "toggle_radial", "Radial")` to `MapScreen.BINDINGS`.
  → red with `extra={'z'}`, which is exactly the "BINDINGS drifted from the single source" defect.
- **Controls:** C-31, C-40, C-18.

#### AT-N03c — filter-then-dispatch (the direct replacement of the old test's *intent*)

- **Observable outcome:** typing a query into the palette narrows the list, and `enter` runs the entry
  the operator can see highlighted — the thing the old test claimed and never did.
- **Pilot chain:** uses an ASCII-only action so every character is a real keypress:
  ```python
  await pilot.press("ctrl+p")
  await pilot.press(*"cobertura")            # real typing, char by char
  await pilot.pause()
  palette = app.screen
  assert [b.action for b in palette._items] == ["coverage"]    # exactly one match, by content
  await pilot.press("enter"); await pilot.pause()
  assert isinstance(app.screen, CoverageScreen)                # the action really ran
  ```
- **RED mutation:** make `palette_items` return `list(KEYMAP)` regardless of query. → the
  `_items == ["coverage"]` arm goes red with 20+ entries, and the `enter` then dispatches the wrong
  action, reddening the `CoverageScreen` arm too.
- **Controls:** C-10, C-16, C-18.

#### AT-N03d — `?` help shows exactly the keys that work on the current screen

- **Observable outcome:** the help overlay on `MapScreen` lists every active-group binding and no
  inactive-group binding. Today `HelpScreen._render_keymap` dumps **all** of `KEYMAP` regardless of
  screen (`mapper/screens/help.py:56-65`), so `plantilla`, `importar csv` and the `palette`-group keys
  are advertised on a screen where they do nothing.
- **Pilot chain:** `await pilot.press("?")`, then read `#help-content`.
- **Oracle:**
  ```python
  shown = help_screen.query_one("#help-content").render().plain
  for b in KEYMAP:
      if b.group in MapScreen.KEY_GROUPS: assert b.label in shown
      else:                               assert b.label not in shown
  assert "plantilla" not in shown and "importar csv" not in shown
  ```
  The loop's set is derived from `KEYMAP` at runtime (C-31); the two explicit names are a
  regression pin on today's measured leak.
- **RED mutation:** revert `_render_keymap` to iterate all of `KEYMAP`. → the `else` arm goes red on
  the first `doors`-group entry.
- **Controls:** C-31, C-40, C-16, C-18.

---

### 2.4 US-N04 — worklist de cobertura

Shipped surface: `CoverageScreen` (`m`) → `MapScreen` + inspector. Target test file:
**`tests/test_worklist.py`**.

#### AT-N04a — `↵` on a coverage row jumps to the node *and* focuses its first missing required field

- **Observable outcome:** after `enter` the cursor is on that node and the keyboard focus is already
  inside the input for the first required field that is empty — not the first field, and not the panel.
- **Why the fixture matters:** in the `legacy` fixture `D` is filled and `O` is the first *missing*
  one. An implementation focusing `schema[0]` would look correct on a naive fixture (C-10).
- **Pilot chain:**
  ```python
  await pilot.press("m"); await pilot.pause()          # coverage report
  await pilot.press("down")                            # real row traversal to 'audit'
  await pilot.press("enter"); await pilot.pause()
  scr = app.screen
  ```
- **Oracle:**
  ```python
  assert isinstance(scr, MapScreen)
  assert scr.nav.cursor == "audit"                       # jumped
  assert scr.focused.id == "insp-field-O"                # focused the first MISSING field
  assert "responsable" in scr.query_one("#inspector").render().plain   # by label, not by 'O'
  ```
  `scr.focused` is read, never set — the focus must be a consequence of the keypress (C-16).
- **RED mutation:** change the focus target from "first field with `required and not value`" to
  `schema[0]`. → the `insp-field-O` arm goes red with `insp-field-D`. Second mutation: revert
  `action_coverage`'s callback to today's body (`mapper/app.py:1424-1428`, cursor only, no focus) →
  the `scr.focused.id` arm goes red because focus is still on the canvas.
- **Controls:** C-10, C-16, C-18.

#### AT-N04b — the worklist affordance cycles next-missing-field across the whole map, and wraps

- **Observable outcome:** repeatedly pressing the worklist key walks every (node, missing required
  field) pair in the map in tree order, then returns to the first.
- **Order definition (must be pinned, or the oracle is unwriteable):** nodes in
  `CoverageScreen._incomplete_nodes()` order (pre-order over the tree, `mapper/screens/coverage.py:99-120`),
  and within a node, `graph.schema` order. Wrap at the end.
- **Fixture:** three incomplete nodes × two missing fields each = **six** stops, deliberately not a
  round number of nodes and with one node whose *first* schema field is filled.
- **Pilot chain:**
  ```python
  await pilot.press("l", "i")
  seen = []
  for _ in range(7):                       # six stops + one to prove the wrap
      await pilot.press("n")               # 'siguiente faltante'
      await pilot.pause()
      seen.append((app.screen.nav.cursor, app.screen.focused.id))
  ```
- **Oracle** — the exact sequence, as content (C-10):
  ```python
  assert seen == [("audit", "insp-field-O"), ("audit", "insp-field-E"),
                  ("b",     "insp-field-D"), ("b",     "insp-field-O"),
                  ("c",     "insp-field-E"), ("c",     "insp-field-C2"),
                  ("audit", "insp-field-O")]      # <- wrapped
  ```
- **RED mutation:** make the cycler advance node-by-node instead of field-by-field (stop at the first
  missing field of each node). → red at index 1: got `("b","insp-field-D")`, expected
  `("audit","insp-field-E")`. Second mutation: `return` instead of wrapping at the end → red at
  index 6 with a repeat of stop 6.
- **Controls:** C-10, C-16, C-18 (boundary: wrap-around).

---

### 2.5 US-N05 — seguridad

Target test file: **`tests/test_destructive_guard.py`**.

#### AT-N05a — `x` on a non-root subtree asks first, and Cancel loses nothing

- **Observable outcome:** a confirmation modal appears naming the node; dismissing it leaves the map
  byte-identical on disk.
- **Measured today:** no modal at all. Probe after `x` on `a` (child `a1`):
  `screen after x: MapScreen`, `on-disk nodes after x: ['b','c','root']` — two nodes destroyed silently.
- **Pilot chain:**
  ```python
  before = (ws / "legacy_nodos.yml").read_bytes()
  await pilot.press("l")                    # cursor on 'a' (which has child 'a1')
  await pilot.press("x"); await pilot.pause()
  assert isinstance(app.screen, _ConfirmScreen)               # asked BEFORE touching anything
  assert "a" in app.screen.query_one("#confirm-text").render().plain
  await pilot.press("escape"); await pilot.pause()            # cancel
  ```
- **Oracle:**
  ```python
  assert (ws / "legacy_nodos.yml").read_bytes() == before     # nothing written
  assert set(MapStore(ws).load("legacy").nodes) == {"root","a","a1","b","c"}
  ```
- **RED mutation:** restore `mapper/app.py:1526`'s `do_archive(True)` for the non-root branch. → the
  `isinstance(_ConfirmScreen)` arm goes red immediately, and the byte-equality arm goes red too.
- **Controls:** C-10, C-12, C-16, C-18.

#### AT-N05b — confirming removes the whole subtree, and only that subtree

- **Pilot chain:** same up to the modal, then `await pilot.press("enter")` (confirm).
- **Oracle:** `set(MapStore(ws).load("legacy").nodes) == {"root","b","c"}` — exact remaining set, so a
  removal that spares the child `a1` or over-deletes `b` is caught. Plus:
  `assert "archivado" in toast_plain`.
- **RED mutation:** change `_remove_subtree` to remove only `root_id` (not the descendants). → red:
  `a1` is still present, leaving an orphan.
- **Controls:** C-10, C-12, C-16, C-18.

#### AT-N05c — undo survives leaving and re-entering the map

- **Observable outcome:** archive a subtree, press `q` back to home, re-open the same map, press `u` —
  the subtree comes back.
- **Measured today:** snapshot depth `1` → `0` across the screen boundary; `u` is a no-op and the data
  is unrecoverable (`nodes after undo on re-entry: ['b','c','root']`). Root cause:
  `self._snapshots` is per-`MapScreen` (`mapper/app.py:1094`).
- **Pilot chain:**
  ```python
  await pilot.press("l", "x", "enter")       # archive 'a' subtree, confirmed
  await pilot.press("q");   await pilot.pause()          # leave the map
  assert isinstance(app.screen, HomeScreen)
  await pilot.press("enter"); await pilot.pause()        # re-open the same map
  assert isinstance(app.screen, MapScreen)
  await pilot.press("u");   await pilot.pause()
  ```
- **Oracle:**
  ```python
  reloaded = MapStore(ws).load("legacy")
  assert set(reloaded.nodes) == {"root","a","a1","b","c"}
  assert reloaded.nodes["a1"].ficha.title == "A Uno"       # the ficha content came back too
  ```
  The second arm matters: a restore that recreates node ids but drops ficha content would pass a
  set-only oracle.
- **RED mutation:** move the undo stack back to `MapScreen.__init__` (`self._snapshots = []`). → both
  arms go red exactly as measured today. Second mutation: have the app-level stack key on the screen
  instance rather than `map_id` → red the same way.
- **Controls:** C-10, C-12, C-16, C-18.

#### AT-N05d — undo with an empty stack is a visible no-op, never a crash

- **Pilot chain:** open a freshly loaded map, make no change, `await pilot.press("u")` **three times**.
- **Oracle:**
  ```python
  assert (ws / "legacy_nodos.yml").read_bytes() == before   # nothing written, not even a re-save
  assert "nada que deshacer" in toast_plain
  assert isinstance(app.screen, MapScreen)                   # still alive
  ```
  Note the byte-equality arm also catches a lazier bug: `_pop_snapshot` calling `store.save` on an
  empty stack and rewriting the file with reordered YAML.
- **RED mutation:** remove the `if not self._snapshots: return` guard
  (`mapper/app.py:1304-1306`). → `IndexError: pop from empty list`, the test errors out.
- **Controls:** C-10, C-16, C-18 (boundary: empty stack).

#### AT-N05e — archiving the root is confirmed with a distinct warning and is undoable

- **Observable outcome:** the root case keeps its own, stronger modal text, and is recoverable.
- **Pilot chain:** cursor on `root`, `x`, read the modal text, `enter`, then `u`.
- **Oracle:**
  ```python
  assert "raíz" in modal_plain          # the root-specific wording, not the generic one
  assert modal_plain != generic_modal_plain_from_AT_N05a
  after = MapStore(ws).load("legacy")
  assert after.root_id is not None and after.nodes                    # map not left headless
  await pilot.press("u")
  assert set(MapStore(ws).load("legacy").nodes) == {"root","a","a1","b","c"}
  ```
- **RED mutation:** collapse both branches into one generic modal. → the
  `modal_plain != generic_modal_plain` arm goes red. Second mutation: skip `_push_snapshot()` on the
  root branch → the final undo arm goes red.
- **Controls:** C-10, C-12, C-16, C-18 (boundary: root node).

---

## 3. The vacuous-test replacement

### 3.1 Diagnosis of `tests/test_palette_dispatches_selected_action`

The test at `tests/test_palette.py:17-46` asserts, as its only real check:

```python
assert not isinstance(app.screen, CommandPalette)
```

It passes today, and it would pass on an implementation where the palette is a completely inert
widget. Here is the chain, each step measured:

1. It types `"add"` into `#palette-input`. Every `KeyBinding.action` in `KEYMAP` is Spanish prose —
   `"agregar hijo"`, `"cobertura"`, `"deshacer"`. `palette_items("add")` filters on
   `q in (binding.key + binding.action).lower()` (`mapper/keymap.py:86-90`); **no entry contains
   `"add"`**, so it returns `[]`.
2. `_refresh_list` therefore appends zero `ListItem`s and skips `list_view.index = 0`
   (`mapper/screens/palette.py:95-96`).
3. `action_run_selected` finds `highlighted_child is None` and takes the early-return branch:
   `self.dismiss(None)` (`mapper/screens/palette.py:106-108`).
4. `MapperApp.action_palette`'s callback receives `None`, hits `if not action: return`
   (`mapper/app.py:1676-1677`), and does nothing.
5. The palette screen popped on dismiss, so `app.screen` is `MapScreen`, so the assertion holds.

The comment above the assertion — *"The action pushed a prompt modal for the child name"* — is false.
No modal was pushed. The test's oracle is satisfied by the palette **closing**, which happens on every
path including total failure. It cannot distinguish "dispatched correctly" from "dispatched the wrong
action" from "dispatched nothing", and it is the reason a 0-of-33 dispatch rate shipped unnoticed.

Three compounding faults, worth naming so they are not repeated:
- **The oracle is a negation of a transient state** (`not isinstance(..., CommandPalette)`), which is
  the weakest possible observable — it is true before the feature exists.
- **The input was never validated.** Nothing asserted `"add"` actually matched something. A one-line
  `assert palette._items` would have caught this in the commit that introduced it.
- **The universal was never stated.** "The palette dispatches" is a claim about all 33 entries; the
  test sampled one, and sampled one that does not exist.

**Verdict: delete it.** It is replaced by `AT-N03a` + `AT-N03c` below, which together assert the
universal *and* the filter-then-run path the old test was reaching for.

### 3.2 Replacement — `tests/test_keymap_conformance.py`

```python
"""Conformance: every keymap entry the palette offers on a screen actually dispatches.

Replaces tests/test_palette.py::test_palette_dispatches_selected_action, which passed
because nothing was dispatched (see .dev-flow/2026-08-25-ui-next-batch-01/01b, section 3.1).
"""
from __future__ import annotations

import pytest

from mapper.app import MapperApp, MapScreen
from mapper.keymap import KEYMAP
from mapper.model import Edge, Ficha, Graph, Node
from mapper.screens.coverage import CoverageScreen
from mapper.screens.palette import CommandPalette

# --- Completeness guards (C-31) -------------------------------------------------
# The universal below quantifies over a set derived from KEYMAP at runtime. If that
# set is ever emptied or silently shrunk, the parametrized test would go green with
# zero cases. These guards make that fail loudly instead.
KEYMAP_BASELINE = 33
EXPECTED_GROUPS = {"app", "doors", "edit", "nav", "node", "palette", "view"}


def test_keymap_completeness_guard():
    assert len(KEYMAP) >= KEYMAP_BASELINE, (
        f"KEYMAP shrank to {len(KEYMAP)} entries (baseline {KEYMAP_BASELINE}). "
        "test_every_palette_entry_dispatches would go vacuous."
    )
    assert {b.group for b in KEYMAP} >= EXPECTED_GROUPS
    for b in KEYMAP:
        assert b.key and b.action and b.group and b.label, f"blank field in {b!r}"
        assert b.action.replace("_", "").isalnum(), (
            f"{b.action!r} is not a method-name suffix -- KeyBinding.action must be "
            "the action method name, not the Spanish UI label (that is KeyBinding.label)."
        )


# --- The universal's input set: DERIVED, never hand-listed (C-31) ---------------
MAP_SCREEN_BINDINGS = [b for b in KEYMAP if b.group in MapScreen.KEY_GROUPS]
assert MAP_SCREEN_BINDINGS, "MapScreen.KEY_GROUPS selected zero bindings from KEYMAP"


def _seed(store, map_id="conf"):
    g = Graph()
    g.add_node(Node(id="root", ficha=Ficha(title="Raíz")))
    g.add_node(Node(id="hijo", ficha=Ficha(title="Hijo")))
    g.add_edge(Edge("root", "hijo"))
    store.save(map_id, g)


@pytest.mark.parametrize(
    "binding", MAP_SCREEN_BINDINGS, ids=lambda b: f"{b.group}-{b.action}"
)
async def test_every_palette_entry_dispatches(tmp_path, monkeypatch, binding):
    """Selecting ANY keymap entry in the palette invokes that entry's action method.

    Only the terminal side effect is stubbed -- the whole dispatch chain the story
    promises (ctrl+p -> list -> real arrow traversal -> enter -> callback -> getattr
    -> call) runs for real (C-16). Per-action semantics are gated by the story ATs.
    """
    method_name = f"action_{binding.action}"
    app = MapperApp(tmp_path)

    owner = MapScreen if hasattr(MapScreen, method_name) else MapperApp
    assert hasattr(owner, method_name), (
        f"palette offers {binding.label!r} (key {binding.glyph}) but neither "
        f"MapScreen nor MapperApp defines {method_name}"
    )

    calls: list[str] = []
    monkeypatch.setattr(owner, method_name,
                        lambda self, _n=method_name: calls.append(_n), raising=True)

    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        _seed(app.store)
        app.push_screen(MapScreen("conf"))
        await pilot.pause()

        await pilot.press("ctrl+p")          # real key, not app.action_palette()
        await pilot.pause()
        palette = app.screen
        assert isinstance(palette, CommandPalette)

        # The empty query lists everything; find where THIS entry landed in the
        # palette's own ordering, then walk there with real arrow keys.
        actions = [b.action for b in palette._items]
        assert binding.action in actions, (
            f"{binding.label!r} is in KEYMAP but the palette did not offer it"
        )
        for _ in range(actions.index(binding.action)):
            await pilot.press("down")
        await pilot.pause()

        await pilot.press("enter")
        await pilot.pause()

    assert calls == [method_name], (
        f"selecting {binding.label!r} dispatched {calls or 'NOTHING'}, "
        f"expected exactly [{method_name!r}]"
    )


async def test_palette_filter_then_dispatch(tmp_path):
    """Typing narrows the list and enter runs the visible entry (AT-N03c).

    This is what the deleted test claimed to do. 'cobertura' is ASCII-only so every
    character is a genuine keypress, and it is the unique substring match.
    """
    app = MapperApp(tmp_path)
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        _seed(app.store)
        app.push_screen(MapScreen("conf"))
        await pilot.pause()

        await pilot.press("ctrl+p")
        await pilot.pause()
        await pilot.press(*"cobertura")
        await pilot.pause()

        palette = app.screen
        assert [b.action for b in palette._items] == ["coverage"], (
            f"query 'cobertura' matched {[b.action for b in palette._items]}"
        )

        await pilot.press("enter")
        await pilot.pause()
        assert isinstance(app.screen, CoverageScreen)


def test_map_screen_bindings_are_generated_from_keymap():
    """AT-N03b: no drift in either direction between KEYMAP and BINDINGS."""
    bound = {b[0] if isinstance(b, tuple) else b.key for b in MapScreen.BINDINGS}
    claimed = {b.key for b in KEYMAP if b.group in MapScreen.KEY_GROUPS}
    assert bound == claimed, f"missing={claimed - bound} extra={bound - claimed}"
    # .key must hold Textual key names, never the display glyph.
    for b in KEYMAP:
        assert b.key not in {"↵", "esc", "/"}, (
            f"{b!r} stores a display glyph in .key; use .glyph for display"
        )
```

**Key idea in one line:** the input set is `[b for b in KEYMAP if b.group in MapScreen.KEY_GROUPS]`
computed at import from the live module and fenced by a `>= 33` completeness guard, the traversal is
real arrow keys through the palette's own ordering, and the oracle is
`calls == [method_name]` — an exact positive identity, so "dispatched nothing" and "dispatched the
wrong action" both fail, which is precisely what the deleted test could not do.

---

## 4. Boundary and negative cases

Every row below is a real parametrized case or a distinct assertion inside the named AT — none is a
"should also test" note (C-18: each AT is one test node driving the whole chain).

| Case | Story | Where it lives | Expected |
|---|---|---|---|
| Empty map (zero nodes) | N01 | `AT-N01d`, param `empty-map` | Inspector shows `(selecciona un nodo)`; `ctrl+s` writes nothing; no exception |
| Node with **no schema** (`graph.schema == []`) | N01 | `AT-N01c`, param `no-schema` | Title/state/notes still editable; zero field rows; no coverage meter; `required_coverage == (0,0)` |
| Required field cleared back to empty string | N01 | `AT-N01d` (primary arm) | Flagged `requerido`; coverage `(1,3)`; key **present** in `fields` with `""` |
| Very long unicode title (2000 chars, combining marks + CJK) | N01 | `AT-N01a`, param `long-unicode` | Truncated **for display only**; disk round-trip returns all 2000 chars byte-identical |
| Title/notes/caption with Rich markup + ANSI + unbalanced bracket | N01 | `AT-N01e` | Rendered literally; no `\[`; no `\x1b`; no payload-derived span |
| Attachment path that does not exist | N02 | `AT-N02d` | Spanish `no existe` toast; opener **not** called |
| `url` attachment (must skip the existence check) | N02 | `AT-N02d`, second arm | Opener **is** called — catches an over-broad guard |
| Malformed attachment kind in `_nodos.yml` (`kind: "wat"`) | N02 | `AT-N02b`, param `bad-kind` | Row renders; `enter` warns and does not call the opener; no crash |
| Zero attachments | N02 | `AT-N02c`, param `empty-list` | Empty-state line; `D` (remove) is a no-op |
| `KEYMAP` emptied / shrunk | N03 | `test_keymap_completeness_guard` | Fails loudly — the universal cannot go vacuous |
| Palette query matching nothing (`"zzzz"`) | N03 | `AT-N03c`, param `no-match` | `_items == []`; `enter` dismisses with `None`; **no** action dispatched (`calls == []`) |
| Duplicate key across groups (`f` = fábrica / foco) | N03 | `AT-N03b`, param `dup-key` | Group-scoped generation binds `f` once per screen; no `DuplicateKeyBinding` |
| Coverage report with everything complete | N04 | `AT-N04a`, param `all-complete` | `(todos los campos requeridos están completos)`; `enter` dismisses with `None`; cursor unchanged |
| Worklist wrap-around past the last stop | N04 | `AT-N04b` (7th press) | Returns to stop 1 |
| Worklist on a map with zero missing fields | N04 | `AT-N04b`, param `nothing-missing` | Toast `sin faltantes`; focus and cursor unchanged |
| Undo with an empty stack, pressed 3× | N05 | `AT-N05d` | `nada que deshacer`; file bytes unchanged; no `IndexError` |
| Archive of the **root** | N05 | `AT-N05e` | Distinct root-specific modal; map not left headless; undoable |
| Archive cancelled | N05 | `AT-N05a` | File bytes byte-identical |
| Archive a leaf (no children) | N05 | `AT-N05b`, param `leaf` | Still confirmed; only that node removed |

---

## 5. Validation method per requirement

| Req | Method | Threshold / criterion |
|---|---|---|
| US-N01 edit + persist | test (pilot) | `AT-N01a`, `AT-N01b`, `AT-N01d` green; **4/4** state branches; **1/1** disk round-trip through unmodified `MapStore.load`; **0** `*.tmp` residue after any save |
| US-N01 label rendering | test (pilot) | `AT-N01c` green; **0** occurrences of a bare schema key letter as a row name in the inspector render |
| US-N01 hostile input | test (pilot) + analysis | `AT-N01e` green (**4/4** arms). Analysis: `grep -c "rich.markup" mapper/inspector.py` == **0**; every file-derived value passes through `darkside.plain` — **100%** of call sites, counted by review |
| US-N02 add / remove | test (pilot) | `AT-N02a`, `AT-N02c` green; exact tuple/list equality on disk |
| US-N02 open — dispatch | test (pilot) | `AT-N02b` green, **2/2** kind arms (`url`, `file`) |
| US-N02 open — actual OS launch | **inspection** (`MAN-01`) | **Not automatable.** Manual: on Windows 11, one `url` and one `file` attachment each open the expected default application. Signed off by the operator, recorded in `04-validation.md`. A green `AT-N02b` is **not** sign-off for this row. |
| US-N03 dispatch universal | test (pilot) | `AT-N03a`: **≥33** KEYMAP entries present (guard) and **100%** of the MapScreen-group subset dispatch — currently **0/33**, so the gate is a hard delta |
| US-N03 BINDINGS generation | test (unit) | `AT-N03b`: symmetric-difference size == **0** (today: 11 missing + 3 extra) |
| US-N03 filter path | test (pilot) | `AT-N03c`: query `cobertura` yields exactly **1** match and dispatches it |
| US-N03 help accuracy | test (pilot) | `AT-N03d`: **100%** of active-group labels shown, **0** inactive-group labels shown |
| US-N04 jump + focus | test (pilot) | `AT-N04a`: focused widget id equals the first *missing* required field — **exact id match**, not "some field" |
| US-N04 worklist cycle | test (pilot) | `AT-N04b`: the observed 7-tuple equals the expected 7-tuple **element for element**, wrap included |
| US-N05 confirmation | test (pilot) | `AT-N05a`, `AT-N05b`, `AT-N05e`: **3/3**; **100%** of destructive entry points (non-root archive, root archive, attachment remove) show a modal — counted against the set of call sites of `_remove_subtree` |
| US-N05 app-level undo | test (pilot) | `AT-N05c`: node set **and** ficha content restored after a screen round-trip; `AT-N05d`: **0** bytes written on an empty stack |
| Regression: existing suite | test | `pytest tests/` — **23 existing tests still green**, minus the 1 deleted vacuous test = **22** must pass, plus the 19 new ATs |
| No prototype coupling | analysis | `grep -rn "prototypes/" mapper/ tests/` → **0** hits |

### Regression checklist (existing flows the change can break)

- [ ] `tests/test_app.py::test_focus_active_blocks_structural_edits` — the inspector must respect
      `_guard_focus_mutation` (`mapper/app.py:1451-1456`); editing while `f`-focus is active must not
      write.
- [ ] `tests/test_app.py::test_plug_repo_url_flow` — `enter` on `#repo-input` must still submit after
      `BINDINGS` are regenerated from `KEYMAP` (the `↵` vs `enter` split is the risk).
- [ ] `tests/test_keymap.py` (4 tests) — `groups_for_keybar` and `palette_items` change shape when
      `KeyBinding` gains `glyph`/`label`; these must be updated, not deleted.
- [ ] `tests/test_coverage.py` — `CoverageScreen._incomplete_nodes` order is now load-bearing for
      `AT-N04b`; pin it.
- [ ] `tests/test_store.py` — `_build_sidecar` must keep round-tripping `attachments` unchanged.
- [ ] `MapScreen.on_mount` cursor resume from `store.last_session()` (`mapper/app.py:1142-1146`) must
      still work after `AT-N05c` moves undo to app level.
- [ ] Search (`/`) still opens `#search-input` — `/` is one of the 11 keys currently absent from
      `BINDINGS` and is bound as `slash`; regenerating from `KEYMAP` must not break it.

### Exit criteria

1. All 19 ATs green, and each has been observed **RED** under its stated mutation before being accepted.
2. `test_palette_dispatches_selected_action` deleted; `AT-N03a` reports 100% dispatch.
3. The 7 regression items above pass.
4. `MAN-01` (attachment opens in the real OS application) signed off by the operator in `04-validation.md`.
5. No unfilled placeholder remains in `04-validation.md`.

---

## 6. Evidence checklist

| # | Item | ✓/✗ | Evidence |
|---|---|---|---|
| 1 | Acceptance criteria use Given/When/Then | ✓ | Rendered as *observable outcome (Given/When implied by the fixture) → pilot chain (When) → oracle (Then)* for all 19 ATs; §2.1–§2.5 |
| 2 | Test cases have explicit Expected, not vague "works" | ✓ | Every oracle is an exact equality or exact count, e.g. `AT-N04b` asserts a 7-tuple element for element; `AT-N02a` asserts `[("url","https://ejemplo.mx/acta.pdf","acta firmada")]` |
| 3 | Edge cases include empty, boundary, invalid, error | ✓ | §4, 19 rows: empty map / no schema / empty attachment list / empty undo stack; 2000-char unicode; malformed `kind: "wat"`; missing path + error toast |
| 4 | Regression checklist exists | ✓ | §5, 7 items, each naming a real existing test or code site (`mapper/app.py:1451`, `1142-1146`) |
| 5 | Exit criteria stated | ✓ | §5, 5 numbered criteria including "observed RED before accepted" |
| 6 | No real PII / secrets | ✓ | Fixtures use `root/audit/a/b/c`, `https://ejemplo.mx/acta.pdf`, `c:/tmp/x.pdf`. No credential, token or client name anywhere |
| 7 | Test-results section left blank | ✓ | This artifact contains no results section; results belong in `04-validation.md`. Measurements quoted here are **defect probes of today's code**, run read-only, clearly labelled "measured" |
| 8 | **C-10** non-default drive, content asserted, one AT per policy branch | ✓ | `AT-N01b` parametrized over 4 states (clamp-to-`ok` mutation reddens 3 of 4); `AT-N04a` fixture fills `schema[0]` so a `schema[0]`-focus bug cannot pass; no `assert x != ""` anywhere |
| 9 | **C-12** output-then-consume via the shipped surface | ✓ | `AT-N01a`/`N01d`/`N02a`/`N02c`/`N05a`/`N05b`/`N05c` all re-read with a **fresh** `MapStore(ws).load(...)`; §2.1 states a test that writes the sidecar directly is a consumer-contract guard, not the gate |
| 10 | **C-16** real mechanism, not a proxy | ✓ | Every chain uses `pilot.press(...)`; `AT-N04a` **reads** `scr.focused` and never calls `.focus()`; `AT-N03a` presses `ctrl+p` instead of calling `app.action_palette()` as `tests/test_palette.py:34` does; §3.2 justifies the one stub (terminal side effect only) |
| 11 | **C-31** universal derived at runtime + completeness guard | ✓ | `MAP_SCREEN_BINDINGS = [b for b in KEYMAP if b.group in MapScreen.KEY_GROUPS]`; `test_keymap_completeness_guard` (`>= 33`, 7 groups, no blank fields); collection-time `assert MAP_SCREEN_BINDINGS` |
| 12 | **C-40** named RED mutation + which arm | ✓ | All 19 ATs; several carry a second mutation reddening a different arm (`AT-N01e` has three: (a) `Static(str)`, (b) re-add `escape`, (c) drop `translate`) |
| 13 | **C-17** hostile-input AT + prescribed construction | ✓ | `AT-N01e`. Measured both defects: rendered plain `'▸ \\[bold red]PWN\\[/] \x1b[31mX…'` (`has backslash-bracket: True`, `has ESC: True`) from `mapper/app.py:1258`. Prescription: `darkside.plain()` + `Text.assemble`, **no** `rich.markup.escape` — justified by the measurement `Text.assemble((escape(h),s)).plain == '\\[bold]…'` vs `Static("[bold red]PWN[/]")` → `plain='PWN'`, `spans=[Span(0,3,'bold red')]` |
| 14 | **C-18** one AT ↔ one on-disk test node | ✓ | 19 ATs → 5 files: `tests/test_inspector.py` (5), `tests/test_attachments.py` (4), `tests/test_keymap_conformance.py` (4), `tests/test_worklist.py` (2), `tests/test_destructive_guard.py` (5). Boundary cases are parametrized cases of a named AT (§4 column 3), never separate partial coverage |
| 15 | **Layer B** black-box through the shipped surface | ✓ | Every AT drives `MapScreen`/`CommandPalette`/`CoverageScreen` via `run_test()`; no AT calls a service method as its primary driver. Boundary + negative evidence in §4 |
| 16 | **Bidirectional surface-reachability** | ✓ | Inputs through the handler: title, state, notes, schema field, attachment add/remove, palette query, coverage row, archive key, undo key. Outputs observed through the handler: `#inspector` render, `#insp-attachments` render, `#help-content` render, `#map-toast` render, `scr.focused.id`, **plus** the on-disk `.mmd`/`_nodos.yml` re-read through the unmodified loader |
| 17 | No unfilled template | ✓ | No `<...>`, no `TC-NNN`, no empty required row. All 19 AT ids enumerated in full — no dotted-range shorthand |
| 18 | Untestable requirement flagged rather than faked | ✓ | §2.2: "Open hands the attachment to the OS default application" has no black-box oracle; the seam is specified, `MAN-01` is logged as **inspection** in §5, and the artifact states a green `AT-N02b` is not sign-off for it |
| 19 | Vacuous test diagnosed and replaced with runnable code | ✓ | §3.1 (5-step chain, `mapper/keymap.py:86-90` → `screens/palette.py:95-108` → `app.py:1676`), §3.2 full pytest module |
| 20 | Prototype untouched; no code changed | ✓ | This artifact is the only file written. Probes were read-only `python -c` / heredoc runs against `tmp` workspaces; `prototypes/` was never opened |
