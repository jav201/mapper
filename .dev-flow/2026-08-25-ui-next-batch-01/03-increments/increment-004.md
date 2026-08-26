# Increment 4 — US-N02 · attachments and the OS-handler boundary

## 1 · What changed

**BLUF: attachments can now be added, opened and removed from the inspector, and the module that
hands a target to the operating system refuses everything outside the workspace BEFORE any launcher
runs.**

- **`mapper/osopen.py` (new)** — one greppable file with one job.
  `open_external(kind, target, *, workspace, launcher=None) -> str` returns a status word and never
  raises for anything a `yaml.safe_load` of a sidecar could produce. It imports nothing from
  `mapper`, so it cannot discover its own targets and the audit surface stays one file.
- **The confinement is the control, and it runs first.** `file` targets resolve against the
  workspace and are refused unless `is_relative_to(workspace)`. **Existence is explicitly not an
  authorisation** — it answers "will this fail?", not "should this open?" — so the containment test
  runs whether or not the path is there.
- **`url` allows only `http`/`https`.** `file:` is refused deliberately: allowing it would hand the
  url branch an unconfined path and route around the workspace check entirely.
- **No shell, ever.** `os.startfile` takes a single path argument; POSIX uses list-form
  `subprocess.run`. No `shell=True`, no `os.system`, no interpolation into a command line.
- **Refusals are visible.** The screen shows the status word; a dropped return value would make a
  refused launch indistinguishable from a successful one.
- **The inspector shows the real target**, not only the caption — a friendly caption over a hostile
  path is how a link lies about where it goes.
- **`DsChip` focused and selected are now distinguishable** (LLR-N06.3, deferred here from Inc-3).
  A single combined branch painted both identically, so "which attachment does the enter key act
  on" was unanswerable from the screen.

## 2 · Files modified

**Source (5 — over the cap of 4, declared).** `mapper/osopen.py` (new), `mapper/app.py`,
`mapper/widgets/inspector.py`, `mapper/widgets/components.py`, `mapper/keymap.py`.

*Why:* `components.py` carries LLR-N06.3, deferred from Inc-3 precisely so it would land with the
attachment chips that are its only consumer. `keymap.py` declares the two new keys — the seat is
the single source of truth, so a key cannot be added anywhere else.

**Tests:** `tests/test_attachments.py` (new, 24 nodes), `tests/test_keymap.py` (fence 22 to 24).

## 3 · How to test

```
PYTHONUTF8=1 python -m pytest -q
PYTHONUTF8=1 python -m pytest -q tests/test_attachments.py
```

## 4 · Test results — one complete run

```
195 passed in 18.70s
```
Ledger: `195 = 171 - 0 + 24`. Reconciles.

**C-40 counterfactual — the confinement control.** Deleting the `is_relative_to` check:

```
FAILED tests/test_attachments.py::test_llr_n02_7_file_outside_the_workspace_is_refused
FAILED tests/test_attachments.py::test_llr_n02_7_existence_is_not_an_authorisation
FAILED tests/test_attachments.py::test_at_n02d_a_refused_attachment_is_reported_not_silently_dropped
3 failed, 21 passed
```
Three arms redden, including the end-to-end one that drives the shipped surface, so the control is
gated at both the unit and the behavioural layer. Restore verified:
`mapper/osopen.py` = `4d07b6a2639355cf1ac38b454d73e8671f563fc7d76a810560e3011db4a697c2`.

**Positive controls are present deliberately.** `test_an_allowed_url_does_reach_the_launcher` and
`test_a_confined_file_does_reach_the_launcher` exist because without them a module that refused
*everything* would pass every refusal test in the file.

## 5 · Risks

| # | Risk | Status |
|---|---|---|
| 1 | The final hop — the OS actually opening the application — has no black-box oracle. | **MAN-01, method `inspection`**, declared in Amendment 1 §A9. `AT-N02b` gates everything up to and including the call to the seam, with the launcher injected. **A green `AT-N02b` is explicitly NOT sign-off for MAN-01**, and the Phase-4 artifact must not count it as covered. |
| 2 | My own counterfactual covers one control. The scheme allowlist and the type guard were not individually mutated by me. | An independent `security-reviewer` sign-off is running against the implementation, tasked specifically with finding a mutation that defeats a control while the suite stays green. Verdict folded before the batch closes. |
| 3 | `kind` is inferred at add time from the presence of a scheme separator. | Crude but conservative: anything without one becomes a `file`, which is the confined branch. A mis-inferred `url` still cannot escape the scheme allowlist. |
| 4 | Symlinks, Windows short names, alternate data streams and UNC paths rest on `Path.resolve()`'s semantics rather than an explicit rule. | Named for the security pass rather than claimed as covered — I did not probe them myself. |

## 6 · Pending items

- MAN-01 inspection record — Phase 4.
- Security sign-off verdict — pending, gating this increment's close.
- Carries unchanged: `MapStore.load` KeyError on a malformed sidecar; the `screens -> app`
  back-edge; the legacy escape call sites.

## 7 · Suggested next task

Increment 5 — US-N04 coverage worklist: `mapper/screens/coverage.py`,
`mapper/widgets/inspector.py`, `mapper/app.py`.

## Evidence checklist

- OK — Tests pass: `195 passed in 18.70s`, §4.
- OK — No secrets in code or output.
- OK — No destructive command without approval; one counterfactual, reverted and hash-verified.
- **FAIL — File count over the cap**: 5 source files against 4. Reason declared in §2.
- OK — Review packet attached.
- OK — Frozen interfaces untouched.
- OK — Dependency ban honoured: `test_osopen_imports_nothing_from_mapper` derives the import list
  from the module's own AST and asserts the walk found imports at all, so an empty parse cannot
  pass it vacuously.
- PENDING — Independent security sign-off; this increment is not closed until it returns.
- OK — Nothing under `prototypes/` modified or staged.
