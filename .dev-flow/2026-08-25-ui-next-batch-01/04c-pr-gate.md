# 04c · PR-level gate — `2026-08-25-ui-next-batch-01`

**Target:** PR #1, `feat/ui-next-batch-01` → `master` · 39 files · +7983 / −319 · 9 commits on the branch
(8 touch `mapper/**` or `tests/**`).
**Gate run:** 2026-08-26, `qa-reviewer`, final PR-level pass over the whole merged diff.
**Verdict: `merge blocked` — 3 HIGH findings.**

Every claim below is an executed probe or a `file:line`. Where I re-derived something the batch
already asserted, I say what I ran, not that it was verified.

---

## 0 · Verdict summary

| # | Finding | Severity |
|---|---|---|
| H-1 | The keymap seat's **key → action pairing** is ungated. A fourth surviving mutation. | **HIGH** |
| H-2 | `darkside.plain()`'s control-character coercion is gated at **one byte** (ESC). A fifth surviving mutation. | **HIGH** |
| H-3 | `AT-N05e` was specified, silently dropped, and **the behaviour it would have caught is broken**: archiving the root empties the map to disk, permanently. | **HIGH** |
| M-1 | `ctrl+s` — a chord bound nowhere on `MapScreen` — is advertised on the batch's primary flow. | MEDIUM |
| M-2 | The **source census** the security sign-off attached to N-2/N-14 was never written and is not in `BACKLOG.md`. | MEDIUM |
| M-3 | `keymap.UNMIGRATED_SCREENS` is dead code; `BACKLOG.md` B-04 claims "two tests fence the list". They fence a different list. | MEDIUM |
| M-4 | Seven sign-off / post-mortem carries are neither fixed nor in `BACKLOG.md`. | MEDIUM |
| M-5 | "Seven defects that already existed on `main`" — one of the seven is provably greenfield, and the causal rider "every one of them" is false. | MEDIUM |
| M-6 | `MAN-01` is disclosed in five artifacts and absent from both summary documents, one of which promises to enumerate open risks. | MEDIUM |
| M-7 | "Review lenses: 5" and "5 HIGH (code review)" rest on artifacts that do not exist in the repo. | MEDIUM |
| L-1 | `AT-N06c` is still carried in `01-requirements.md` as an owned AT; no such node exists and the matrix does not record the substitution. | LOW |
| L-2 | Post-mortem test ledger `88 → 210 (+123, −6)` is arithmetically 205. | LOW |
| L-3 | Post-mortem says "7 commits"; 8 touch code, 9 exist. | LOW |
| L-4 | Post-mortem says Inc-3 touched 5 source files; it touched 6. | LOW |
| L-5 | Traceability matrix's "each mapping to exactly one node" is true of test *functions*, not node ids. | LOW |
| L-6 | `BACKLOG.md` B-07's line numbers are stale after `930dfa6`. | LOW |

**Items that came back clean:** frozen interfaces (§3), flakiness (§5), hygiene (§7), and the
27 ATs the traceability matrix does list (§1).

---

## 1 · Dual traceability, re-derived from `pytest --collect-only`

I did not read the matrix's generation claim; I re-derived the mapping and then compared.

```
PYTHONUTF8=1 python -m pytest --collect-only -q   → 210 tests collected
grep -oE "test_at_n0[0-9][a-z]" | sort -u | wc -l → 27 distinct AT functions
```

**Result — the matrix's 27 rows are honest.** Every `AT` id in
`06-docs/traceability-matrix.md` resolves to a test function that really exists in the collected
suite. No row claims a node that is not there. The "generated from the collected pytest nodes"
claim holds for what it lists.

**But the matrix is incomplete against the spec.** Extracting AT ids from each artifact:

| Artifact | AT ids present |
|---|---|
| `01-requirements.md` | N01A–E, N02A–D, N03A–E, N04A–C, **N05A–N05E**, **N06A–N06D** |
| `01b-acceptance-design.md` | N01A–E, N02A–D, N03A–D, N04A–B, **N05A–N05E** |
| `04-validation.md` | 27 ids — matches the suite |
| `06-docs/traceability-matrix.md` | 27 ids — matches the suite |
| **collected suite** | 27 ids |

Two ids appear in `01-requirements.md` and resolve to **nothing on disk**:

- **`AT-N05e`** → finding **H-3** below. Not a bookkeeping slip.
- **`AT-N06c`** → finding **L-1** below.

Per-story black-box coverage (US-N01…US-N05, HLR-N06): every story has at least one AT that
resolves to exactly one on-disk node. **US-N05's set is one AT short of its own specification.**

### L-5 · "exactly one on-disk node" is loose

The matrix states "**27 acceptance tests, each mapping to exactly one node**". True at the level of
test *functions*; three ATs are parametrized and expand to many node ids:

```
test_at_n01b → 4 node ids
test_at_n03a → 48 node ids
test_at_n03f → 8 node ids
```

Defensible reading, but "node" is the word `pytest` uses for the expanded id. Worth one clause.

---

## 2 · Suite, run by me

`PYTHONUTF8=1 python -m pytest -q` → **`210 passed`**, exit 0. Count read from my own run, and
reproduced 7 times (§5). Collected = 210, passed = 210, so nothing is skipped or deselected.

---

## 3 · Frozen interfaces — clean

Signatures compared `master` → `HEAD` directly, not read from a report:

| Frozen surface | Result |
|---|---|
| `IRenderer.render` impls (`layered`, `outline`, `radial`, `lane`) | **signatures identical** |
| `Graph` (`mapper/model.py`) | **class body identical** (diff of the `class Graph` region is empty) |
| `MapStore` (`mapper/store.py`) | file unchanged in the diff |
| `Canvas` (`mapper/canvas.py`) | file unchanged |
| `mermaid.parse` / `mermaid.dump` | file unchanged |
| `GitHubConnector.fetch` | file unchanged |
| `save_svg` / `save_png` | file unchanged |

`mapper/model.py` is the only frozen-adjacent file touched: a **purely additive**
`Ficha.missing_required(...)` (`model.py:41-48`). `Ficha` is not on the frozen list and nothing was
altered or removed. `LayeredRenderer.render`'s **body** changed (the duplicate ficha strip was
deleted, `views/layered.py:225`) with the signature untouched — the correct way to do it, and the
in-code comment says so.

**Zero frozen-interface changes. The post-mortem's "Frozen-interface changes | 0" is TRUE.**

---

## 4 · Gate carries

The full ledger is long; the discharged majority is not reproduced here. Verified discharged
include U-B4, U-M1, U-M2, U-M5, LLR-N06.3, S-M6, MAN-01's inspection record, and sign-off blockers
N-1, N-2, N-3, N-4, N-7, N-12, N-13. Properly carried into `BACKLOG.md`: S-M5→B-01, ARQ A-7→B-02,
legacy escape sites→B-03, unmigrated screens→B-04, Amendment-3 canvas tone→B-05, N-6/N-8/N-9/N-10→
B-06, N-14 remainder→B-07, N-4 refusal shape→B-08, and process lessons P-01…P-05.

The `(partial)` in commit `930dfa6` covers exactly N-14's nine remaining sinks, and **that
remainder is properly recorded** as B-07. N-12 and N-13 are fully done.

### M-2 · The census test the sign-off conditioned its fix on was never written

`04b-security-signoff.md` asks for it twice — once under N-2 ("gate it with a census test over
`mapper/` asserting every `notify(` call carrying file-derived text passes `markup=False`") and
again under N-14, with the reason: "**the wording is what let this recur twice**".

```
grep -rn "census\|markup=False" tests/     → zero hits
```

`930dfa6` broadened LLR-N01.11's wording and fixed some call sites. It added no census. So the nine
known-uncoerced sinks in B-07 are held open by **a list in a markdown file rather than a test** —
which is precisely the failure mode the sign-off named. Neither fixed nor in `BACKLOG.md`.

### M-3 · `UNMIGRATED_SCREENS` is dead, and the backlog says otherwise

```
grep -rn "UNMIGRATED_SCREENS" mapper/ tests/  → mapper/keymap.py:39  (its own definition, only)
```

`BACKLOG.md` B-04 states "`keymap.UNMIGRATED_SCREENS` names them; **two tests fence the list**", and
`increment-001.md` §8 says it "stopped being decoration". Both are false in the tree. The two tests
(`tests/test_keymap.py:164` and `:193`) quantify over **`TAB_BINDING_EXCEPTIONS`** — a different,
two-element tuple. A screen silently leaving or joining the seat is **not** fenced by anything.

### M-4 · Carries that are neither fixed nor in `BACKLOG.md`

| id | Raised | What it is |
|---|---|---|
| M-W | signoff §9.4, §9.7 | `scheme.startswith(ALLOWED_SCHEMES)` survives the suite. C-4 **explicitly banned** prefix matching; nothing gates the ban. `tests/test_attachments.py:168-176` has no `http`-prefixed non-allowed scheme param. |
| M-X | signoff §9.4, §9.7 | Control guard narrowed to NUL survives — only payload is `chr(0)`. (Independently confirmed as **H-2** on the other side of the boundary.) |
| M-Y | signoff §9.4, §9.7 | Control guard applied only to `kind == "url"` survives; no `kind="file"` control-char arm. |
| M-AE | signoff §9.4 | `root = Path(workspace)` unresolved survives. Fails closed, but the sign-off recorded live breakage: "`mapper maps` with a relative argv would refuse every attachment". |
| N-11 | signoff §9.6 | Labelled "Carry (informational)". B-06 carries exactly four minors; N-11 is not among them. |
| §2.6 | postmortem | "A counterfactual that never ran was nearly filed as evidence." §2.1–2.5 each got a P-0x line; §2.6 got none — although Inc-3 §4 says it was "the third time in this batch". |
| Inc-1 §1 | increment-001 | `ctrl+s → save` / `tab → toggle_preview` "removed from the *seat*, not from the app: they still work, but nothing advertises them any more … **recorded as a carry**". No backlog line covers live-but-unadvertised bindings. Ambiguous — B-04 is adjacent but is about a different property. |

---

## 5 · Flakiness — clean

`AT-N04a`'s 1-in-3 failure does not reproduce. There is no ordering plugin installed
(`pytest_randomly`, `pytest_random_order`, `pytest_xdist` all absent), so default runs share one
deterministic order; I varied it explicitly.

| Run | Order | Result |
|---|---|---|
| 1–4 | default | `210 passed` ×4 |
| 5–6 | default | `210 passed` ×2 |
| 7 | **files reversed** (`test_worklist_safety.py` first, `test_app.py` last) | `210 passed` |
| `AT-N04a` ×20 | isolated, fresh process each | **20/20 passed** |

**7 full-suite runs, 0 failures, 0 errors, no non-determinism in any test.** The gate is not flaky.

---

## 6 · Test quality, adversarially — a fourth *and* a fifth surviving mutation

Both were executed, both left the suite fully green, both were reverted and verified by sha256, and
`__pycache__` was purged.

### H-1 · The seat's key → action pairing is ungated *(fourth surviving mutation)*

**Mutation** — in `mapper/keymap.py`, swap only the `action` field of two entries:

```python
KeyBinding("u", "u", "collapse_branch", "deshacer", "node"),   # was "undo"
KeyBinding("z", "z", "undo", "plegar rama", "view"),           # was "collapse_branch"
```

**Result: `210 passed in 22.31s`.** Fully green.

**Why the existing controls miss it.** `tests/test_keymap.py` is a genuinely strong file — the
per-scope size fence, the `inspect.unwrap` check against inherited Textual plumbing, and the
positive control for `duplicate_chords()` are all real. But its two universals are orthogonal to
each other and neither pins the pairing:

- `AT-N03a` proves each declared `action` **exists** on the owning class.
- `AT-N03f` proves each declared `key` is **bound** on the owning class.
- Nothing proves that key *K* dispatches the action the seat advertises **for K**.

Swapping two actions keeps both sets identical, so both universals hold. `glyph`, `label`, `group`
and the per-scope counts are all untouched, so the completeness guard, the glyph test and
`groups_for_keybar` all hold too.

**Why nothing else catches it.** Across the whole suite only **11 distinct keys** are ever pressed:

```
enter(5) ctrl+p(4) x(3) y(2) m(2) escape(2) R(2) question_mark(1) q(1) n(1) I(1)
```

against 25 `map`-scope bindings. `u` is never pressed — every undo test invokes
`screen.action_undo()` directly (`tests/test_worklist_safety.py:214`, `:232`, `:258`). So the seat
entry that reaches undo is white-box only.

**The user-visible consequence.** The keybar, palette and help all render `label`, which stays with
the key. After the mutation the operator sees `u  deshacer` and pressing `u` folds a branch; they
see `z  plegar rama` and pressing `z` silently performs an **undo** — destroying the last edit. This
defeats US-N03's entire premise, and it lands on the one control that US-N05 depends on for
recovery. Note that `x` (archive) *is* partly protected because AT-N05a/b press it for real; the
recovery key is not.

**Suggested fix (for `software-dev`, not applied here):** extend `AT-N03f` to compare
`{(key, action)}` pairs rather than key sets — Textual's merged bindings expose the action name, so
this is the same shape of assertion the test already makes, at one more field of resolution.

### H-2 · `darkside.plain()`'s coercion is gated at exactly one byte *(fifth surviving mutation)*

`plain()` is the single coercion helper every renderer of sidecar text must pass through
(`darkside.py:276`). It has **zero direct tests** — `grep -rn "plain(" tests/` returns 0 hits.

**Mutation** — `mapper/darkside.py:272-273`:

```python
_CONTROL_MAP = {0x1B: "�"}          # was: 0x00–0x1F minus tab/LF, plus 0x7F–0x9F
```

**Result: `210 passed in 22.94s`.** Fully green.

**Demonstrated harm under the mutation:**

```
NUL      survives_verbatim=True   repr='titulo\x00X'
BEL      survives_verbatim=True   repr='titulo\x07X'
CSI-C1   survives_verbatim=True   repr='titulo\x9bX'
OSC-C1   survives_verbatim=True   repr='titulo\x9dX'
ESC      survives_verbatim=False  repr='titulo�X'
```

`0x9B` is the single-byte C1 **CSI** and `0x9D` the C1 **OSC** — so a C1-based escape sequence in a
ficha title reaches the compositor verbatim, which is exactly the threat `darkside.py:268-271`
names ("An ANSI cursor-move or an OSC-52 clipboard write inside a ficha title reaches the
compositor verbatim").

**Why the control misses it.** `AT-N01e` is a good test — it covers the unmatched closing tag, the
no-backslash direction, and asserts the replacement char is present rather than the character
merely dropped. But its only control-character payload is `\x1b` (`tests/test_inspector.py:186`).
One byte of a 63-byte class.

This is the **same class the security sign-off already flagged as M-X and M-Y** and left ungated
(M-4 above) — flagged there on `osopen.py`'s guard, unflagged here on the rendering guard. Two
independent surfaces, one untested coercion policy.

**Suggested fix:** a direct parametrized test over `plain()` covering NUL, BEL, ESC, `0x7F`, `0x9B`,
plus the tab/newline pass-through — the boundary the map actually declares.

### Controls I attacked and could **not** break

Stated so the negative result is on the record:

- **`mapper/osopen.py` confinement.** Genuinely well-defended. `tests/test_attachments.py` already
  covers the sibling-prefix bypass (`maps-exfil`, `:116-119`), absolute paths outside the workspace
  (`:74-95`), `..` traversal (`:33-48`), the non-existent-file case (so existence is not treated as
  authorisation), directory targets, and the `file:` scheme routing around the URL branch. The test
  file documents its own RED mutations. I found no cheap substitution.
- **`AT-N06a`** (focus signal). Not vacuous: asserts ACCENT spans are **empty** while unfocused and
  **non-empty** once focused, plus the hint naming the region. A always-ACCENT mutation reddens the
  first assertion. Amendment 3's weakening is honest and the test does not overreach.
- **Vacuous-assertion sweep.** I scanned the six new/changed test files for tautologies and
  assertions that pass against an empty or default value. The `== []` shapes are all paired with a
  positive control or a fixture that makes the empty case meaningful (e.g.
  `launcher.calls == []` alongside a refusal status word). The two deleted/rewritten legacy tests
  (`test_coverage.py`, `test_legacy_fixture.py`) were replaced with strictly stronger assertions.
  No vacuous test found among the additions.

### H-3 · `AT-N05e` was dropped without record, and the behaviour is broken

`AT-N05e` is not a stub. It has a full specification in
`01b-acceptance-design.md` ("**AT-N05e — archiving the root is confirmed with a distinct warning and
is undoable**"), it is listed in `01-requirements.md`'s C-21 re-cut table as one of Inc-6's ATs, and
it is a named validation threshold:

> `AT-N05a`, `AT-N05b`, `AT-N05e`: **3/3**; **100%** of destructive entry points (non-root archive,
> root archive, attachment remove) show a modal

It exists in **no test**, appears in **neither** `04-validation.md` nor the traceability matrix, and
is in **no** `BACKLOG.md` line. The "3/3" and "100% of destructive entry points" threshold is
therefore reported against a set that was quietly reduced to 2.

**And the feature it would have gated is broken.** Executed probe (root cursor, `x`, read modal,
confirm, reload from disk):

```
--- BEFORE ---   nodes: ['a','b','b1','root']   root_id: root
--- MODAL ---    '¿archivar la raíz «erp» y sus 3 descendientes? esto reemplazará la raíz del mapa.'
--- AFTER  ---   nodes: []   root_id: None   edges: []
--- AFTER UNDO - nodes: ['a','b','b1','root']  root_id: root
```

Three things, in order of severity:

1. **The map is left headless and empty**, which is the exact condition AT-N05e's §4 row named:
   "*Distinct root-specific modal; **map not left headless**; undoable*". `root_id` is `None` and
   zero nodes remain.
2. **The state is persisted to disk before the operator can react.** `app.py:1744` calls
   `self.store.save(...)`; my probe read the empty graph back through a fresh
   `MapStore(tmp_path).load(map_id)`.
3. **Recovery is in-memory only.** `undo_stacks` is a plain dict created in the App's `__init__`
   (`app.py:1943`) and read at `app.py:1458`. Undo does restore the map *within the session* — but
   quitting after archiving the root loses it permanently.

The modal is also actively misleading: it promises "esto **reemplazará** la raíz del mapa" (*this
will **replace** the root*). Nothing is replaced; everything is deleted. On the batch's own
standard — a refusal must be distinguishable from a success — a confirmation that misdescribes its
outcome is worse than no text at all.

The distinct-root-message half of AT-N05e (`app.py:1756-1760`) *was* implemented. Only the test was
dropped, and it is the half that would have caught the other two clauses.

---

## 7 · Hygiene — clean

| Check | Result |
|---|---|
| Control bytes `< 0x20` other than tab/LF/CR, all 39 diff files | **none** — the two committed NULs are gone and none survive |
| Secrets in added lines (`api_key`, `token`, `ghp_`, `sk-…`, `AKIA…`, PEM headers) | **none** — only fixture names (`secret.txt`) and traversal payloads (`/etc/passwd`) |
| Tracked files matching `.gitignore` (`git ls-files -i --exclude-standard`) | **none** |
| `mapper.db` / `*.db` / `*.sqlite` tracked | **none** |
| `prototypes/` in this PR's diff | **none** — the 24 tracked prototype files all pre-date this branch; no commit in `master..HEAD` touches any `prototypes/` path |
| `prototypes/ui_next/` | untracked, as found. Not touched by this gate. |

### Environment note (not a PR defect)

`core.autocrlf=true` with no `.gitattributes`; every working-tree file is LF. A `git checkout` of a
single file rewrites it to CRLF, which is how ` M mapper/keymap.py` can appear in `git status` with
`git diff` empty. I hit this while reverting a probe and restored the exact original bytes —
`sha256 5da6a934…` matches my pre-mutation baseline, and worktree/index/HEAD all hash to blob
`99fcd5a3…`. **No content was changed by this gate.** Adding a `.gitattributes` would stop this
recurring; that is a repo-hygiene suggestion, not a finding against this PR.

---

## 8 · Docs vs code

### M-5 · "Seven defects that already existed on `main`"

Claimed at `05-postmortem.md:5-6` and, in Spanish, at `06-docs/executive-summary.md:38-40`.

**One of the seven is provably not pre-existing.** Row 7, path traversal — "*Se abrieron `calc.exe`
y `powershell.exe` desde un mapa*":

```
git show master:mapper/osopen.py                          → does not exist on master
git grep -nE "startfile|xdg-open|webbrowser" master -- mapper/  → zero hits
```

There is no file-launching code path on `master` **at all**. The batch's own
`01b-acceptance-design.md` calls it "**greenfield**", and `02b-security-review.md` scopes the finding
to "*The PDR signature*" — i.e. it was caught in the batch's own unshipped design, before it
shipped. That is a genuinely good catch and it belongs in the post-mortem's separate "found in code
the batch itself wrote" category, not in the pre-existing count.

**The causal rider is false.** Both documents claim *every one* of them "lived in the gap between
'the action ran' and 'the key the operator presses reaches the action'". The post-mortem's own
attribution table contradicts this two pages later: the keybar-truncation row was found by
**measuring painted cells** (216 at a hard-coded 118) and the traversal row by **executing a
filesystem attack**. Neither involves a key reaching an action.

**The number is also unstable across the batch's own artifacts:** `04-validation.md` says "**five**
defects that existed before it started", plus two from the security lens. The post-mortem promotes
that to seven. Meanwhile the batch documents roughly **21** distinct pre-existing defects across
`01-requirements.md`, `01b`, `02b` and `02c` — three of which (`MapStore.load` `KeyError`, the
`factory.py:343` back-edge, ~20 legacy escape sites) the post-mortem itself carries forward as
unfixed pre-existing problems *while excluding them from its count of pre-existing defects found*.

The client-facing `executive-summary.md` carries the same number in Spanish. Under GRNDIA's
"never present assumptions as facts", this needs correcting before the summary is delivered.

### M-6 · `MAN-01` is absent from both summary documents

The batch handles `MAN-01` **correctly** where it declares it. `06-docs/traceability-matrix.md:45`
is exemplary: method `inspection`, in a table explicitly titled "Verification that is NOT a test",
with "**a green `AT-N02b` is not sign-off for MAN-01**" in bold. It is **not** counted among the 27.
Same in `01-requirements.md`, `01b`, `increment-004.md` and `04-validation.md` §5.

**It then disappears from the two documents a reader outside the batch actually reads.** `grep` for
`MAN|inspecc|inspection` over `05-postmortem.md` and `06-docs/executive-summary.md` returns one hit,
and it is the substring `MAN` inside `COMMAND_PALETTE_ENABLE`.

No sentence in either document counts `MAN-01` as tested — on the narrow question, both pass. The
problem is the omission colliding with the executive summary's own promise:

> **Riesgos abiertos, declarados y no cerrados en silencio:** un archivo lateral mal formado
> todavía puede impedir cargar un mapa completo; cuatro pantallas modales aún no leen la
> declaración única de teclas; y quedan detalles de seguridad menores registrados como pendientes
> explícitos.

That sentence claims to enumerate what remains open. An acceptance row that no test gates belongs
in it — as does the security sign-off that `04-validation.md` records as "⚠ pending here rather
than assumed". Neither is listed, while `executive-summary.md` presents "los adjuntos se abren
desde ahí" as delivered and `05-postmortem.md` counts "Stories delivered | 5 of 5 P1".

### M-7 · Two claimed review lenses have no artifact

`05-postmortem.md` states "Review lenses | **5** (architect, qa, security ×2, ux, code-review)" and
"Blocking findings from review | **5 HIGH (code review)** + 2 blockers".

The batch directory contains `01b` (qa), `02b` + `04b` (security ×2) and `02c` (ux). There is **no
architect artifact and no code-review artifact**. The 2 security blockers are confirmed
(`04b` §6). The "5 HIGH (code review)" count rests on nothing checkable.

I am **not** asserting those lenses never ran — they may have run as subagents without writing a
file. I am asserting the claim is unverifiable from the repo, in a document whose sibling states
"Every claim above cites a command output, a `file:line` or a collected node id." Either land the
artifacts or soften the claim.

### Verified-true numeric claims

For balance, these check out: `88 → 210` (master has exactly 88 test functions); `0 of 33` palette
entries (`git show master:mapper/keymap.py | grep -c "KeyBinding("` → 33); `9 of 17` keybar
shortcuts; `216 cells at 118`; 13 premises / 11 held; 10 of 30 undeclared files; 12 counterfactuals;
3 reviewer mutations that left the suite green; 3 amendments; **0 frozen-interface changes**;
4 unmigrated modal screens; `prototypes/ui_next/` never staged.

### Low-severity numeric corrections

- **L-2** — "88 → 210 (**+123, −6** superseded)": 88 − 6 + 123 = **205**. The figure was carried
  over from `04-validation.md`, where it correctly described a 205-test run before `930dfa6` added
  five. True delta is **+128**.
- **L-3** — "committed across **7 commits**": 8 commits touch `mapper/**` or `tests/**`; 9 exist on
  the branch.
- **L-4** — "Increments 2, 3 and 4 touched **6, 5 and 5** source files against a cap of 4": Inc-3
  (`0b69fe2`) touched **6** (`app.py`, `darkside.py`, `keymap.py`, `widgets/chrome.py`,
  `widgets/inspector.py`, `widgets/rail.py`). Actual is 6, 6, 5. The section exists to disclose a
  budget breach honestly and under-reports the largest one.
- **L-6** — `BACKLOG.md` B-07 cites `:1671 :1673`; after `930dfa6` inserted three lines at `:1133`
  the export sink moved to `:1679` and `:1673` no longer exists. The other seven line numbers still
  match and are still uncoerced.

### L-1 · `AT-N06c`

`01-requirements.md` still reads: "HLR-N06 … owns `AT-N06a` …, `AT-N06c` (`tab` traverses; no screen
binds it), `AT-N06d` … Owning increments: … Inc-1 (`AT-N06c`)."

No `AT-N06c` exists. The *requirement* is genuinely discharged — Amendment 2's LLR-N06.5 records
"Discharged in Inc-1 by construction" and two real tests exist
(`tests/test_keymap.py:159` and `:164`). So this is a documentation slip, not a coverage hole. But
the substitution of an AT by two unit tests is nowhere recorded in the matrix, and the requirements
document still presents `AT-N06c` as a live owned AT. One line in the matrix's "Verification that is
NOT a test" table would close it.

---

## 9 · M-1 · A dead chord on the batch's primary flow

`mapper/app.py:1640-1643`, inside `_goto_gap` — the worklist jump that `AT-N04a` gates:

```python
if missing:
    self.query_one(HintLine).set_hint(
        f"completa «{missing[0].label}» · esc deja el campo", "ctrl+s"
    )
```

`darkside.hint_line(text, key)` renders that second argument visibly in `INK` (`darkside.py:178-179`).

```
grep -rn "ctrl+s" mapper/ --include=*.py
  mapper/app.py:1642            ← the hint
  mapper/screens/editor.py:23   ← EditorScreen, an UNMIGRATED modal
  mapper/screens/editor.py:83
```

**`ctrl+s` is bound nowhere in `map` scope.** So every time the operator jumps to a coverage gap —
the US-N04 → US-N01 path, the batch's headline flow — the UI tells them to press a chord that does
nothing on that screen.

This also contradicts the batch's own ruling. Amendment 2's **U-M3** resolved three contradictory
commit protocols with "**Ruling: `↵`/blur commits**", retiring `ctrl+s`. The `esc` half of that
ruling was implemented (`widgets/inspector.py:43`, `"salir del campo"`); the `ctrl+s` half was not.

`AT-N04a` asserts the cursor moves and focus lands on the first missing field. It does not assert
what the hint line advertises, so the dead chord ships green. This is precisely the defect class
US-N03 exists to eliminate, on the flow the batch exists to make trustworthy.

---

## 10 · What would clear this gate

Blocking (HIGH):

1. **H-1** — extend `AT-N03f` to pin `(key, action)` pairs, not key sets. Re-run the `u`/`z`
   action-swap mutation and confirm it reddens.
2. **H-2** — add a direct parametrized test over `darkside.plain()` covering NUL, BEL, ESC, `0x7F`,
   `0x9B`, and the tab/newline pass-through. Re-run the `_CONTROL_MAP = {0x1B: …}` mutation and
   confirm it reddens.
3. **H-3** — decide and record what archiving the root *should* do, then write `AT-N05e` against it.
   If the map must not be left headless, the current behaviour is a bug to fix, not a test to write
   around. At minimum the modal must stop saying "reemplazará" when it deletes. If root archive is
   intentionally out of scope, withdraw `AT-N05e` **in writing** and correct the "100% of
   destructive entry points" threshold in `01b`.

Should ride along (MEDIUM), in rough cost order: **M-1** (one-line hint fix + an assertion in
`AT-N04a`), **M-3** (either fence `UNMIGRATED_SCREENS` or correct B-04), **M-5**/**M-6**/**M-7**
(correct the two summary documents before the executive summary is delivered), **M-2** and **M-4**
(write the census test, or record all seven carries in `BACKLOG.md` — the discipline the batch
otherwise held well).

LOW items are editorial and need not block anything.

---

## Evidence checklist

- [x] Acceptance criteria use Given/When/Then — inherited from `01b-acceptance-design.md`; this is a
      gate report over existing ATs, not new criteria.
- [x] Test cases have explicit Expected, not vague "works" — every probe in §6 states the exact
      expected vs observed (`210 passed`, `nodes: []`, `root_id: None`, byte-level repr output).
- [x] Edge cases include empty, boundary, invalid, error — §6 covers empty (`AT-N05d` empty undo
      stack, reviewed), boundary (control-byte class limits `0x1B` vs `0x9B`), invalid (root
      archive), error (refusal paths in `osopen.py`).
- [x] Regression checklist exists — §3 frozen interfaces + §5 reverse-order run + §2 full-suite
      count serve as the cross-increment regression gate.
- [x] Exit criteria stated — §10.
- [x] No real PII / secrets — §7; scan returned only fixture names.
- [x] Test results section reflects runs I actually executed — 7 full-suite runs, 20 isolated
      `AT-N04a` runs, 2 mutation runs, 1 behavioural probe. Nothing is reported that I did not run.
- [x] **Layer B (black-box):** every story's deliverable observed through the shipped surface —
      done via `pilot.press` paths and on-disk `MapStore.load` reads. **This is where H-1 and H-3
      come from:** the undo seat entry and the root-archive outcome are *not* observed through the
      shipped surface anywhere in the suite.
- [x] **Bidirectional surface-reachability:** input dimensions and output deliverables exercised
      through the handler — checked; the gap is recorded as H-1 (11 keys pressed vs 25 map
      bindings) and H-2 (`plain()` never called directly by any test).
- [x] **No unfilled template** — no placeholders remain; every row is an executed result.

**Gate discipline:** two source mutations were applied and reverted. `mapper/keymap.py` restored to
sha256 `5da6a934a56b635e8dca0c4cce0fe1f70741e6da7ad30fd896aed7c60e29d3fe`; `mapper/darkside.py` to
`29c302469d96ebeff03d1cead8ca4bb7f6206193cc825c1df6f05e7b50c2d8b4`. Both verified with
`sha256sum -c`, both confirmed against HEAD by `git hash-object`. `__pycache__` purged. No file
under `prototypes/` was read or written. This report is the only file this gate created.
