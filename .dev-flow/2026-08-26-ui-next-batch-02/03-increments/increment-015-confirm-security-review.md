# Security Review — Increment 015 · `Inc-CONFIRM` (part 1) · `HERMETIC-1` + `B-68`

| Field | Value |
|---|---|
| Batch | `2026-08-26-ui-next-batch-02` (sealed) · FULL protocol per ruling `D35` |
| Reviewer | `security-reviewer`, independent, on the frozen tree |
| Base | `a552783` + staged `tests/test_hermetic.py` |
| Date | 2026-09-19 |
| **Verdict** | **BLOCK — 2 HIGH** (`F1`, `F2`) |

Everything below was MEASURED on this tree. No repo file was edited; every probe
was written and run out of repo under `C:\Users\jjgh8\clde\`.

---

## Scope reviewed

`mapper/app.py` (the only source file), `pyproject.toml`, `tests/conftest.py`,
`tests/test_hermetic.py`, `tests/test_app.py`, `tests/test_pan.py`,
`tests/test_search.py`, `tests/test_a3_census.py`; plus, as the blast radius of
the change rather than as diff, `mapper/export.py`, `mapper/views/layered.py`,
`mapper/views/state.py`, `mapper/canvas.py`, `mapper/osopen.py`.

Read first and not re-litigated: the packet, `state.json`
(`hermetic_defects[0]`, the `B-68` block, `controls_for_engineering_rules`),
`01-requirements.md` amendment set 7 / `A-99`. **The ruling that `B-68` is in
scope is taken as given. What is judged here is the FIX.**

---

## Findings

### F1 — The outgoing artifact is re-wrapped at 200 columns, so a full-extent export SCRAMBLES the map  [Severity: HIGH]

- **What:** `mapper/export.py:17` builds the export console at a hard-coded
  `width=200`. The fix at `mapper/app.py:3540-3556` grows the rendered canvas
  to the map's full extent — measured at **241 columns for a 21-node map** and
  at **48,013 columns for the packet's own 4001-way fanout**. Rich folds every
  canvas row that exceeds 200 columns into stacked 200-column chunks, in
  row-major order. The tree's geometry — which card hangs under which connector
  — is destroyed, while the file remains a well-formed SVG containing every
  title. **This is `B-68`'s own failure class, one layer down: the artifact
  looks complete to sender and recipient and misrepresents the map.**
- **Where:** `mapper/export.py:17` (`Console(record=True, width=200, ...)`)
  against `mapper/app.py:3540-3556` (the extent growth), consumed at
  `mapper/app.py:3472`.
- **Measured (threshold):** no fold at 16 leaves (canvas 193 cols); **fold at
  20 leaves** (canvas 241 cols → 21 canvas rows become 25 emitted SVG lines);
  at 40 leaves, 21 rows → 33 lines; at 200 leaves, 7 non-blank rows → 86 lines
  (**×12.3**). Probe: `C:\Users\jjgh8\clde\sec_b68_threshold.py`,
  `C:\Users\jjgh8\clde\sec_b68_wide_artifact.py`.
- **Measured (the scramble itself), root + 20 leaves, canvas 241×25** — probe
  `C:\Users\jjgh8\clde\sec_b68_scramble.py`:

  rendered picture (what `B-68` promises the recipient):
  ```
  row 4:     ┌───────────┬───────────┬── … ──┬─────┴─
  row 5: ▐ rama0     ▐ rama1     ▐ rama2 … ▐ rama9
  ```
  the artifact that leaves the machine:
  ```
  line 5: '┌───────────┬───────────┬─── … ───┬─────┴─────'
  line 6: '─────────┬───────────┬───────────┐'
  line 7: '▐rama0▐rama1▐rama2 … ▐rama15▐'
  line 8: 'rama16▐rama17▐rama18▐rama19'
  ```
  The bus tail is printed as its own line above the cards; the last four cards
  sit on a separate line below the first sixteen.
- **Why it matters:** the increment's stated deliverable is "the recipient wants
  the MAP". Above ~17 leaves the recipient does not get the map; they get a
  fold-wrapped transcript whose adjacency is wrong. A third party reading the
  SVG can draw incorrect conclusions about parent/child relationships, and
  neither the operator nor the recipient has any signal that the picture was
  folded. The pre-fix export was sized from the TERMINAL, so the fold was
  reachable only on a >200-column terminal; this increment makes it the normal
  case for any non-trivial map.
- **Reachable today:** yes, with no excursion — open any map with ≥ ~17 leaves
  and press `e`. The batch's own headline benchmark (4001-way fanout, 48,013
  columns) is 241 folds deep per row.
- **Why the lane is green anyway:** both `B-68` acceptance arms drive
  `tests/inc3_support.pan_graph()`, whose full-extent canvas measures **120
  columns** — below the 200-column fold threshold. The arms are true in the one
  band where the defect cannot appear, and `test_b68_…_carries_nodes_the_
  viewport_could_not_hold` asserts only PRESENCE of titles, which folding
  preserves. Verified: `C:\Users\jjgh8\clde\sec_b68_artifact_shape.py` — 35
  canvas rows → 35 emitted lines, ratio 1.0.
- **Recommendation (not applied — `software-dev` applies it):** size the export
  console from the Text it is given rather than from a constant, and extend one
  acceptance arm to a fixture above the threshold so the band is covered.
  ```python
  # mapper/export.py
  def save_svg(text: Text, path: Path | str) -> None:
      lines = text.plain.split("\n")
      width = max(20, max((len(line) for line in lines), default=20))
      console = Console(record=True, width=width, height=max(1, len(lines)),
                        file=io.StringIO())
  ```
  Note this widens `F2` rather than relieving it; the two must be decided
  together.

### F2 — Full-extent export turns a terminal-bounded render into an INPUT-bounded one on the message pump, and the declared worst case is not the worst case  [Severity: HIGH]

- **What:** `mapper.canvas.Canvas.rows()` (`mapper/canvas.py:167-170`) is a
  dense `for y in range(h): for x in range(w)` loop, so the export's cost is the
  BOUNDING-BOX AREA of the map, not its node count. Before this increment the
  area was bounded by the terminal; after it, the area is chosen by the map
  file. `action_export_svg` (`mapper/app.py:3466`) is **synchronous**, so the
  whole cost is paid on the Textual message pump: no progress, no cancel, no
  confirmation.
- **Where:** `mapper/app.py:3466` + `mapper/app.py:3540-3556`;
  `mapper/canvas.py:167-170`.
- **Measured end to end** (render + `save_svg` + write, probe
  `C:\Users\jjgh8\clde\sec_b68_real_cost.py`):

  | map | nodes | export canvas | cells | wall clock | peak Python heap | artifact |
  |---|---|---|---|---|---|---|
  | fanout 300 + chain 300 | 601 | 3601×1208 | 4.35 M | **20.0 s** | 41 MB | 1.4 MB |
  | fanout 600 + chain 600 | 1201 | 7201×2408 | 17.3 M | **75.8 s** | 155 MB | 2.8 MB |
  | fanout 900 + chain 900 | **1801** | 10801×3608 | 39.0 M | **169.1 s** | **363 MB** | 4.2 MB |

  Cost is linear in cells (measured across the three points). The worst shape
  inside `MAX_RENDER_NODES = 12000` is wide AND deep at once — fanout 6000 +
  chain 5999 → canvas **72001×24004 = 1.73 billion cells** (probe
  `C:\Users\jjgh8\clde\sec_b68_cost_and_convergence.py`), which extrapolates
  from the measured points to **≈125 minutes and ≈16 GB of heap** — i.e. an
  OOM after a multi-minute freeze on any ordinary machine.
- **Why it matters:** the packet declares this risk but with the wrong figure.
  §6 item 1 says "synchronous, **14.42 s worst case measured**" and routes a
  "responsiveness question" to the whole-branch gate. The real figure at an
  ordinary 1,801-node map is **169 s**, and the real worst case inside the
  product's own node cap is **hours plus a 16 GB allocation**. A coordinator
  deciding on 14.42 s is deciding on a number that is wrong by 12× at an
  ordinary size and by ~500× at the cap. **A risk declared with the wrong
  worst case is a risk that has not been declared**, and this batch's own
  catalog says a prediction is measured, never labelled.
- **Input trust:** this project's own threat model states that a map "arrives
  with a cloned or shared map" and that sidecar content is untrusted
  (`mapper/osopen.py:1-15`). A shared `_nodos.yml` therefore chooses the work
  the operator's app performs, with one keystroke and no interrupt.
- **Reachable today:** yes — open a wide-and-deep map, press `e`. The UI is
  frozen until it completes; the operator's only exit is killing the process.
- **What is NOT wrong:** the growth loop is sound. It converges in **2 steps**
  on every shape probed (fanouts 500/4001/11999, chains 4000, combined
  wide+deep, 40-character titles), never oscillates despite `card_w` being
  non-monotone in `w`, and maps above `MAX_RENDER_NODES` degrade to a fitting
  box in 1 step. `EXPORT_EXTENT_STEPS = 6` is real headroom, not a silent crop
  waiting to happen. The `except Exception` fallback at `mapper/app.py:3543-3549`
  is correctly scoped.
- **Recommendation (not applied):** a cap that REFUSES is not a crop. Compute
  the area before rendering and, above a declared budget, decline with a named
  toast (`"mapa demasiado grande para exportar: N celdas"`) instead of freezing
  — the operator is TOLD, which is the whole distinction `B-68` turns on. If
  the export must always succeed, move it off the message pump with a progress
  and a cancel. Either way, correct §6 item 1's figure before the coordinator
  rules on it.

### F3 — The transient class is closed for three fields of five; `selected_id` and `hits` still ride into the artifact  [Severity: MEDIUM]

- **What:** the ruling is about a CLASS — transient view state must not be
  encoded in a standalone artifact. `ViewState` has nine fields
  (`mapper/views/state.py`): `selected_id, w, h, focus_owner, hits, diff,
  pan_x, pan_y, folded`. `_export_view_state` neutralises exactly three
  (`mapper/app.py:3534-3536`). Measured, by exporting the same graph with only
  one field varied (probe `C:\Users\jjgh8\clde\sec_b68_session_state.py`):

  | field | artifact changes? | what the recipient sees |
  |---|---|---|
  | `selected_id` | **yes** | the cursor node painted `bold GROUND on ACCENT` |
  | `hits` | **yes** | search highlight, plus a hit-count tail on every fold pill |
  | `folded` | **yes** | the folded subtree is ABSENT (declared by a `+N` pill) |
  | `focus_owner` / `pan_x` / `pan_y` | no | correctly neutralised |

- **Where:** `mapper/app.py:3532-3537`; painted at `mapper/views/layered.py:687-696`
  (selection block) and `mapper/views/layered.py:645-669` (fold pill hit count).
- **Why it matters:** two of these are the operator's SESSION, not the map.
  `hits` is the resolution of whatever the operator last typed into search, so
  the artifact silently tells the recipient what the sender was looking for —
  including a numeral, the per-branch hit count, printed next to folded
  branches. `selected_id` is worse for a specific reason created by the fix
  itself: because `focus_owner` is forced to `""`, the export takes the
  `("", "canvas")` branch and paints the cursor node in the **ACTIVE** tone, so
  a standalone file asserts an emphasis that came from where the cursor
  happened to rest. The `focus_owner` ruling's own argument ("which screen
  region owns the keyboard is meaningless inside a file") applies verbatim to
  "where the cursor was".
- **Reachable today:** yes — search for anything, or simply move the cursor,
  then press `e`.
- **Recommendation:** extend the same `replace()` to `selected_id=None` and
  `hits=frozenset()`, or record a coordinator ruling that selection and search
  highlighting are DELIBERATE export content. `folded` needs no change: the
  omission is declared in-band by the `+N` pill, which is the artifact telling
  the recipient what is missing — the property `B-68` was about.
- **Note for the packet:** §1 states the fix "neutralises `focus_owner`,
  `pan_x` and `pan_y` together" and §4b claims the class. The field-level claim
  is true; the CLASS claim is not.

### F4 — The full-extent export pulls in diff content the screen was not showing  [Severity: MEDIUM]

- **What:** `pan_extent` sizes the vertical extent as
  `tree_bottom + removed_h + pill_h` (`mapper/views/layered.py:401-412`), so the
  export now grows the canvas specifically far enough to include the
  `eliminados` ghost strip — the titles of nodes that exist only in the
  revision being compared against. Measured (probe
  `C:\Users\jjgh8\clde\sec_b68_diff2.py`): a 12-deep chain with one removed
  node, at the declared context-of-use canvas 58×25 — on screen `"eliminados"`
  and the removed title are **not visible**; in the export canvas (60×56) both
  are **present**.
- **Where:** `mapper/views/layered.py:401-412` and `mapper/views/layered.py:675-685`.
- **Why it matters:** this is the inverse risk of the defect, and it is real:
  content the operator could not see at the moment of export now leaves the
  machine. The content is a previous revision's node titles — for a consulting
  deliverable that can be a dropped scope item, a renamed client, an internal
  label. Nodes scrolled off-screen are the operator's own current map and are
  the point of the fix; folded subtrees are correctly NOT added (measured, F3);
  the diff ghost strip is the one genuinely new category.
- **Mitigating, and why this is not HIGH:** the strip is labelled `eliminados`
  in the artifact, so the omission-turned-inclusion is declared in-band to the
  recipient; and diff inclusion in exports was already ruled deliberate (`B-50`).
  The party surprised is the SENDER, not the reader.
- **Reachable today:** yes — `d` to diff, `e` to export, on any map taller than
  the canvas.
- **Recommendation:** either state in `A-99` that the export deliberately
  includes the diff's removed-node strip, or suppress the ghost strip when the
  state is an export state. A one-line ruling is enough; what is not enough is
  silence.

### F5 — The lane guard can be walked past silently, and the lane's green now asserts hermeticity  [Severity: MEDIUM]

Executed against the real `tests/conftest.py` from a scratch session outside
the repo (`C:\Users\jjgh8\clde\sec_guard_probe\`, `test_bypass.py` +
`test_precise.py`). Each row is a call form a future test could use.

| form | verdict | note |
|---|---|---|
| `subprocess.run(["gh", …])` / `Popen` | **REFUSED** ✓ | the instrument works |
| `["gh.exe"…]`, absolute path, `./gh`, `GH` | **REFUSED** ✓ | `_executable` normalisation is correct |
| `git -c k=v fetch`, `--git-dir=… fetch`, `-C x -c a=b pull` | **REFUSED** ✓ | the `-C`-value bug the packet reports finding is genuinely fixed |
| `from subprocess import run` | **REFUSED** ✓ | caught via the patched `Popen` underneath |
| **`from subprocess import Popen`** | **SILENT BYPASS** ✗ | **measured: the process actually spawned** |
| `subprocess.run("gh api …", shell=True)` | **SILENT BYPASS** ✗ | declared in the packet §5 |
| `os.system("gh api …")` | **SILENT BYPASS** ✗ | **not declared anywhere** |
| `curl` / `wget` / `ssh` / `pip` / `python -c` | **SILENT BYPASS** ✗ | `_ALWAYS_REMOTE` is `{"gh"}` only (`tests/conftest.py:42`) |
| `urllib.request.urlopen(...)` | **SILENT BYPASS** ✗ | in-process HTTP is invisible to the guard AND to the AST census |

- **Where:** `tests/conftest.py:42`, `:55-66` (`_executable` returns `""` for a
  `str`/`bytes` argv), `:103-147` (`monkeypatch.setattr(subprocess, "run"/"Popen")`),
  and `tests/test_hermetic.py::_derived_spawn_executables` (walks only
  `subprocess.<spawn>` receivers under `mapper/`).
- **Why it matters:** `HERMETIC-1`'s declared axis is "no UNDECLARED EXTERNAL
  DEPENDENCY", but what is enforced is "no `gh`, and no seven `git`
  subcommands, spawned through two module attributes". A guard that can be
  walked past is worse than no guard when the lane's green is read as the
  hermeticity claim — which is exactly how this packet reads it (§4, "the axis
  is held too"). The `urllib` row is the sharpest: `mapper/github.py` already
  imports from `urllib`, so a future connector that drops the `gh` CLI for an
  HTTP client would restore the original defect with every arm still green and
  the census still complete.
- **Reachable today:** not by an operator — this is reachable by the next test
  author, which is the population the control exists for. It does not change
  the product's behaviour.
- **Recommendation:** (a) narrow the claim in the packet and in
  `tests/conftest.py`'s header from "the default lane may not reach the
  network" to what is enforced; and (b) close the cheap half — add the
  common remote binaries to `_ALWAYS_REMOTE` (`curl`, `wget`, `ssh`, `scp`,
  `nc`, `pip`, `npm`), and REFUSE rather than pass a `str`/`bytes` argv
  (a shell string that cannot be tokenised is precisely the case that must not
  be waved through). The `from subprocess import Popen` and `urllib` holes need
  a socket-level guard (e.g. patching `socket.socket.connect`) if the axis is to
  be held rather than sampled; that is a scope decision, not a one-liner.

### F6 — The guard raises `TypeError` on the legal `subprocess.run(args=[...])` keyword form  [Severity: LOW]

- **What:** `guarded_run(argv, *args, **kwargs)` (`tests/conftest.py:134`) takes
  `argv` positionally only. Measured:
  `TypeError: _hermetic_lane.<locals>.guarded_run() missing 1 required
  positional argument: 'argv'`.
- **Why it matters:** fail-LOUD, so no test reaches the network through it, but
  it false-fails a correct offline call written in a legal form and the error
  names an internal closure rather than the rule. The negative control
  (`test_the_guard_does_not_false_fail_local_git`) does not cover this form.
- **Recommendation:** `def guarded_run(argv=None, *args, **kwargs)` with
  `argv = argv if argv is not None else kwargs.get("args")`.

### F7 — Viewer launches declared unguarded: the declaration is ADEQUATE  [Severity: LOW — NOTE, not a blocker]

- **Judged, not assumed.** `VIEWER_LAUNCH_UNGUARDED` in `tests/test_hermetic.py`
  declares that nothing stops `os.startfile` / `open` / `xdg-open`
  (`mapper/osopen.py:47-55`). That declaration is about the TEST LANE, and the
  product-side control it might be mistaken for is present and strong:
  `open_external` refuses non-`http(s)` schemes, refuses URL userinfo, refuses
  C0/C1 control characters, and confines `kind == "file"` to the workspace
  BEFORE any launcher runs, with existence explicitly not treated as
  authorisation.
- **Residual:** if a future arm drives `open_external` without injecting
  `launcher=`, a real viewer launches on the developer's machine. Offline, low
  blast radius, and no arm reaches one today. Declared and classified is the
  right treatment; **this does not block.**

### F8 — Secrets: clean  [Severity: LOW — NOTE]

- Scanned the full diff for token/key/password/bearer/`ghp_`/`github_pat`/
  private-key/`.env` patterns: **zero hits**. `.gitignore` already covers
  `.env`, `.env.*`, `*.svg`, `*.png`, `*.db` and `.mapper/`, so exported
  artifacts and local session state cannot be committed.
- `test_repo_screen_two_pane_renders` no longer drives a live repository; its
  fixture is a two-node synthetic graph. The string `jav201/taskboard` remains
  as an identifier in the fixture and in the classifier's parametrisation —
  a public repository name, pre-existing in the tree, not a credential.
- `gh` credentials are held by the CLI and never touched by product code.
  `GitHubError(exc.stderr.strip())` surfaces `gh`'s stderr into a UI toast;
  pre-existing, not in this diff, and `gh` does not echo tokens in stderr —
  noted only so the next reviewer does not have to re-derive it.
- **Disclosure:** proving the `from subprocess import Popen` bypass caused one
  real `gh api x` invocation from my probe session — an unauthenticated-shaped
  404 GET against `api.github.com` under the operator's own CLI credentials.
  No data was read or written. It is named here so a stray line in an audit log
  has an owner.

---

## Verdict

- [ ] OK to ship
- [ ] `BLOCK-UNTIL: …`
- [x] **Block — 2 HIGH findings open (`F1`, `F2`)**

`F1` and `F2` are both properties of the artifact and the act that produces it,
both introduced or materially widened by this increment, both reachable today
with one keystroke, and neither covered by the acceptance arms. `F1` means the
increment does not deliver its own deliverable above ~17 leaves; `F2` means the
packet's declared worst case is wrong by 12× at an ordinary map size and by
roughly 500× at the product's own node cap, which disarms the very gate the
packet routes it to.

**This verdict authorises nothing.** It is not a deploy approval and it does not
close `Inc-CONFIRM`; it returns the increment to the operator. No mitigation in
this report has been applied, and none may close a HIGH until it is applied AND
verified by a further pass.

Per the batch's own rule, `F3`–`F8` are recorded and do not block. `F3` and `F4`
each want a one-line ruling more than they want code.

---

## Evidence states

| Item | State |
|---|---|
| `F1` fold threshold + scramble | `executed` — `sec_b68_threshold.py`, `sec_b68_scramble.py`, `sec_b68_wide_artifact.py`, `sec_b68_artifact_shape.py` |
| `F1` mitigation (console sized from the Text) | `planned` — drafted, NOT applied, NOT verified |
| `F2` cost measurement (3 real points + extrapolation) | `executed` — `sec_b68_real_cost.py` |
| `F2` convergence / `EXPORT_EXTENT_STEPS` headroom | `executed` — `sec_b68_cost_and_convergence.py`, 2 steps on every shape probed |
| `F2` mitigation (declared refusal or off-pump render) | `planned` — NOT applied |
| `F3` per-field artifact diff | `executed` — `sec_b68_session_state.py` |
| `F4` diff-ghost inclusion | `executed` — `sec_b68_diff_content.py`, `sec_b68_diff2.py` |
| `F5` guard bypass matrix | `executed` — `sec_guard_probe\test_bypass.py`, `test_precise.py` |
| `F6` keyword-form `TypeError` | `executed` — `sec_guard_probe\test_precise.py` |
| `F7` viewer-launch declaration | `approved` — judged adequate; product-side control read and verified present |
| `F8` secret scan | `executed` — zero hits over the full diff |
| Full default lane re-run | `not-run` — 332 s, and no finding here depends on it; the lane's own green is `F5`'s subject, not its evidence |
| Prior `B-68` security finding (S-D surface 4) | `executed` — the pan/geometry defect it named IS closed; the fix's own consequences are `F1`/`F2` |

Probes live under `C:\Users\jjgh8\clde\` (out of repo — this batch declares no
`artifact_homes.evidence`, the same declared gap the packet records in §6 item 3).

## Evidence checklist

- [x] Each finding has what · where · why · recommendation — `F1`–`F8`.
- [x] Each finding has a severity rating — 2 HIGH, 3 MEDIUM, 3 LOW/NOTE.
- [x] No secret values appear in this output — locations only; `F8` names no value.
- [x] Verdict is explicit, and each HIGH carries measured evidence with NO applied-and-verified mitigation — hence Block, not `BLOCK-UNTIL`.
- [x] New tool/integration scope and blast radius addressed — no new MCP/Composio/third-party connector is added by this increment; the one external surface it touches (`gh` via `GitHubConnector`) is REMOVED from the default lane, which narrows blast radius. `F5` states what the replacement guard does and does not enforce; `F7` states the viewer-launch surface.
