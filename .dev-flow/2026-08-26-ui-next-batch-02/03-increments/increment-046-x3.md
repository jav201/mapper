# Increment 046 -- Inc-X3: an attachment chip opens with real keys and a real click (INC9P-UX-F1)

Batch `2026-08-26-ui-next-batch-02`, branch `feat/ui-next-batch-02`, base `f06f8ee`. Authority: `A-128` (appended to `01-requirements.md`, dated 2026-10-02) and `VERDICT-inc9-2026-09-30.md` Round 13, X3. 1 source file.

## 1. What changed

- Confirmed root cause: `DsChip.Changed(selected)` carried no widget, and `FichaInspector.on_ds_chip_changed` reads `event.control`. In Textual 8.2.8 `Message.control` is a property returning `None` unless a subclass defines it, so `hasattr` is True, the value is `None`, `widget_id` is empty, the `insp-att-` prefix test fails and the handler returns silently (no toast, nothing opens). `enter`, `space` and a click all go `DsChip.action_activate` -> `Changed`, so all three were dead. Earlier arms posted `AttachmentActivated` directly and never crossed that hop.
- Fix (`mapper/widgets/components.py`, source 1 of the cap of 2): `DsChip.Changed.__init__(self, chip, selected)` stores `self.chip`; a `control` property returns it; `action_activate` posts `Changed(self, self.selected)`. `FichaInspector` is unchanged. The open-time path policy is untouched.
- Tests: `tests/test_inc9x3.py` (new, ASCII, 14 items). Records: `A-128`, this file.

## 2. Files modified

Source: `mapper/widgets/components.py`. Tests: `tests/test_inc9x3.py` (new). Docs: `01-requirements.md` (append `A-128`), `increment-046-x3.md` (new). **1 source file, within the cap of 2.** Sealed arms changed: none. `state.json` and `BACKLOG.md` not touched.

## 3. Arm table (RED/GREEN)

RED = commit `086c746` (arms as strict xfail; source byte-identical to `f06f8ee`, checked with `git diff --stat f06f8ee HEAD -- mapper` = empty) in a separate `git worktree` under `%TEMP%` (removed), temp HOME, `--runxfail`: **14 failed**. Without `--runxfail` the same tree reports `14 xfailed` (0 XPASS). GREEN = `b4ccca9`: **14 passed**.

| Arm (118 and 87 each; real input only; launcher stubbed) | RED on `f06f8ee` (measured) | GREEN |
|---|---|---|
| `tab` to the file chip `docs/x.pdf`, then `enter` / `space` (4 items): launcher called once with the resolved inside path, and the `#map-toast` strip reads `abierto` + the caption | failed: `[] == ['<tmp>\docs\x.pdf']` (launcher never called) | pass |
| real click on the file chip (2 items): same result | failed: same | pass |
| `tab` to the URL chip, `enter` / `space` (4 items): the URL launcher path receives the URL, toast `abierto` | failed: `[] == ['https://example.com/acta']` | pass |
| sidecar attachment `C:\outside\x.pdf`, `enter` or click (4 items): the V1 sentence is the only toast, launcher not called | failed: `[] == [V1]` (silent) | pass |

At 87 the inspector is hidden until `I`: the arms press `I` first (declared). The `tab` count to the chip is not hard-coded (6 presses at 118 and 5 at 87 with this map's schema field `D`, measured by a probe; the 87 count matches the task's "tab x5"): the helper presses `tab` until `app.focused.id` is the chip, bounded at 12, and fails loudly otherwise. Regression: the existing attachment arms that post the message stay green (section 5).

## 4. Mutant table

Harness `%TEMP%\x3-harness\mut.py` (outside the repo): byte-level read and write in the file's own line endings (all three files CRLF; every mutated text uses `\r\n` where it spans lines), sha256 pin checked before each mutation and after each restore, the verdict printed before the restore, `-B`, `-W error::SyntaxWarning`, suite `tests/test_inc9x3.py` (not `-x`; the failed names listed are all that failed). Pins (the `b4ccca9` files): `components.py 06f77b4318350023bbd5936101ca6126ea070fc77a52101c1fab2b91d3caad9d`, `inspector.py 2ace7f91d3bdb9463413b67ab24e0a54e94c931b071a06fbf6ad049cceb519f6`, `app.py df9839393c334ab516c774644813a63d1d23923b8389854925ba231d72628df2`. All pins re-checked after the run: OK. **7 mutants run, 7 killed, 0 survived.**

| # | Arm claimed | Exact text -> mutant text | Result |
|---|---|---|---|
| M1 | `Changed.control` returns the chip | `            return self.chip` -> `            return None` (components.py) | 14 failed (every arm) |
| M2 | `enter` activates | in `DsChip.on_key`, `if event.key in {"space", "enter"}:` -> `if event.key in {"space"}:` (components.py; anchored on the `Changed(self, self.selected))` and `refresh` lines above it, since another widget has the same line) | 6 failed: file-enter x2, url-enter x2, refusal-enter x2 |
| M3 | `space` activates | same line -> `if event.key in {"enter"}:` | 4 failed: file-space x2, url-space x2 |
| M4 | a click activates | `    def on_click(self) -> None:` then `        self.action_activate()` -> body `        pass` (components.py, anchored on the `DsChip` lines above) | 4 failed: file-click x2, refusal-click x2 |
| M5 | the chip index is read from its id (the URL chip is index 1) | `index = int(widget_id[len("insp-att-") :])` -> `index = 0`, in `on_ds_chip_changed` (inspector.py, anchored on the lines that follow) | 4 failed: both URL arms x 2 sizes x 2 keys |
| M6 | a file attachment outside the workspace is refused by real input | `refusal = _path_refusal(att.path, self.store.workspace) if att.kind == "file" else None` -> `refusal = None` (app.py, anchored on the next two lines) | 4 failed: refusal x4 |
| M7 | the success toast appears | `self._event_toast("abierto", darkside.plain(att.caption or att.path))` -> `pass` (app.py) | 10 failed: file-key x4, file-click x2, url-key x4 |

Not mutated (declared): a double launch (it would show as a two-item list, but no mutant doubles it); the `I` key at 87 (if `I` did not show the inspector the chip would be unreachable and `_focus_chip` would raise; no mutant measured it). M5, M6 and M7 mutate `inspector.py` and `app.py` in the harness only; this increment changes neither file.

## 5. Test results

- `tests/test_attachments.py tests/test_components.py tests/test_inspector.py tests/test_inc9x3.py tests/test_inc9n.py`: **182 passed** in 113 s (`-W error::SyntaxWarning`, temp HOME).
- Ruff 0.8.4, `ruff check mapper tests --output-format json --no-cache`, a clean `f06f8ee` worktree under `%TEMP%` (removed) vs this tree, a programmatic set difference on (file relative to its root, code, message): **26 entries on each side, both differences empty.**
- Render, the success toast after `enter` on the file chip at 118x34 (the bottom rows of the screen; the launcher stub received `<tmp>\ws\docs\x.pdf`):

```
| ▰▱   1/2|
| abierto   plan|
|next ▸ j/k/h/l move · ↵ open card · / search|
|move j next sibling  k previous sibling  h parent  l child  ↵ open card  / search  n next match … +26  ? all keys|
```

- Environment: temp HOME and USERPROFILE, git identity from environment variables, no network, loopback, UNC, device or real cache, no real gh; the launcher was a recording stub in every arm and in the render, so nothing was opened; the pytest rootdir was the repo or a scratch worktree only; scratch worktrees removed. The staged diff was grepped for the account name (read at run time, not printed) and for literal Cf characters before each commit: 0 hits.

## 6. Risks, unmeasured, next

- Risks: (1) `DsChip.Changed` changed its constructor (`chip` first). The only poster is `action_activate`; no test or other module constructs it (grep). (2) Activating a chip still toggles `selected`, so the chip is painted as selected after opening; pre-existing, out of scope. (3) The only reader of `event.control` in `mapper/` is `on_ds_chip_changed` (grep); `on_ds_segmented_changed` reads `event.index`, so the other `Ds*` messages have no consumer of the same gap.
- Unmeasured: POSIX; a real terminal's mouse reporting (Pilot's click is synthetic); the final hop to the OS (MAN-01, the launcher is stubbed).
- Suggested next task: the coordinator closes `INC9P-UX-F1`.

## Commits

- `086c746` the arms, strict xfail.
- `b4ccca9` the fix (1 source file; `OPEN_STEPS` emptied).
- the records (`A-128`, this file).

## Full-lane result

`2648 passed, 24 deselected, 3 xfailed` (0 failed) in 1328 s (22 min), `python -m pytest -rf -q -W error::SyntaxWarning`, uninterrupted, on `2fa4845`, with a temp HOME and a git identity from the environment, run as the last step. Baseline 2634/0; the delta is the 14 new `test_inc9x3.py` items. The 3 xfailed are pre-existing. A first attempt of the lane ran WITHOUT the git identity in its environment (my omission) and reported 5 failed in `tests/test_github.py` (`git commit` exit 128, "Author identity unknown"); it was discarded and the lane re-run once, as above. After this section was appended only this `.md` changed; the lane was NOT re-run.
