# Security Pass 3 — Inc-3 fix round 2 (`feat/ui-next-batch-02`, uncommitted over `954f8f3`)

## VERDICT: **SIGN-OFF — 0 HIGH**

**Scoped pass, not a re-review.** The five questions put to me were re-executed rather than read.
All five resolve in the author's favour.

**The F-A routing is honest.** The arm drives the real crash, `strict` is set, and I reproduced the
mechanism by which the marker cannot be left behind: fixing F-A in an export turns the arm
`[XPASS(strict)] -> 1 failed, exit 1`. The two claims the routing rests on — F-A is pre-existing at
`954f8f3`, and it subsumes `SEC-F1`'s attack — are both **true, measured, and discriminating**.
`inspector.py`, `coverage.py`, `factory.py` and `store.py` are **byte-identical** to `954f8f3`.

**This increment is safe to commit with F-A routed rather than fixed.** No new HIGH. Nothing in
round 2 adds a leak, an unguarded pump path, or a process/network/dependency surface.

**One caveat that is about the commit itself, not about security:** the new artifact code-point scan
carries a non-vacuity clause that is coupled to *git tracking state*, and it **goes red the moment
this batch is committed**. Measured, not predicted. Fix it in the same commit — see `P3-F1`.

---

## Scope reviewed

`.dev-flow/…/increment-003-security-confirmation.md` (findings) and `increment-003.md` §12 (round-2
claims), against the uncommitted working tree at `C:\Users\jjgh8\Github\mapper`. Questions 1–5 only.
Not re-checked, per the ruling: `SEC-F1`, `SEC-F2`, the breadcrumb, the `_branch_coverage_glyph`
hang, the three guard placements, the `A-89` attribute-form derivation.

**The shared working tree was never written to**, except this one report file.

| Check | Result |
|---|---|
| Where the work ran | `tar` export of the working tree at `…/scratchpad/mapper_copy` with its own `git init` (about 25 census arms shell out to `git ls-files`), plus a second `git archive 954f8f3` export at `…/scratchpad/base954` for the pre-existence reproduction |
| Green baseline before any mutant | `796 passed, 17 deselected, 1 xfailed` in 104.44 s, **exit 0** — matches §12.6 exactly. Slow lane `17 passed, 797 deselected` in 28.72 s, **exit 0** |
| Restores | 12 mutants applied, **12 of 12 restored, sha256 `OK`, 0 `MISMATCH`** |
| Shared-tree digests at close | `outline.py 74604dbfdb6d35c3` · `radial.py def09fbe114af7e5` · `rail.py 508b5d5d1ebc644a` · `inspector.py 2ace7f91d3bdb946` · `factory.py 771a15e3c418b4c8` · `coverage.py 63cf11a4a01b8f8a` — **all six identical to the previous pass's reported digests**. Only `app.py` (`f90835563212f2a0 -> a8e3753530724b80`) and `layered.py` (`d4d82a2052a198da -> 815a337927e673df`) moved: exactly the two round-2 source files. **No third source file moved.** |
| `git status` at close | 31 entries, 5 untracked — identical to session start |

**No banned code point is spelled into this file or into any file I wrote.** Every payload was built
with `chr(0x…)` at run time and is named below by code point and position only.

> One measurement artifact, so it is not mistaken for a finding: the previous pass's `git show`-based
> digests for `inspector.py` et al. differ from a raw `sha256sum` of the working file purely because
> of CRLF normalisation. Compared correctly — `git archive 954f8f3` against the working tree, raw
> bytes — all four are **byte-identical**, and `git diff 954f8f3 -- <file>` is empty for each.

---

## 1 · Is the F-A routing honest, or does it launder the obligation?

### **HONEST. The obligation is mechanically enforced, not merely documented.**

**The arm drives the real crash, not a proxy.** Run with `--runxfail` so the failure is visible
rather than absorbed:

```
BadIdentifier: 'insp-field-<U+0001>' is an invalid id; identifiers must contain only
letters, numbers, underscores, or hyphens, and must not begin with a number.
  textual/dom.py:99 in check_identifiers   <- reached from FieldInput.__init__
```

That is `F-A`'s exact mechanism — `inspector.py:137-140` interpolating `SchemaField.key` into a
Textual widget id — reached through the shipped map-open path, not simulated.

**All three named keys kill the app independently, and the discrimination is real.** Driven one key
per app instance, on the post-fix tree:

| Key (by code point / position) | `app.is_running` | Exception |
|---|---|---|
| `chr(0x01)` | **False** | `BadIdentifier` |
| `"a" + chr(0xF1) + "o"` (`año`) | **False** | `BadIdentifier` |
| `"fecha" + chr(0x20) + "limite"` | **False** | `BadIdentifier` |
| `chr(0x202E)` | **False** | `BadIdentifier` |
| `chr(0x200B)` | **False** | `BadIdentifier` |
| **control** — `"obs"` (identifier-safe) | **True** | none |

The control matters: it is not that everything crashes. The arm's claim that an ordinary Spanish
schema key is enough is confirmed, so this is a defect and not hardening.

**`strict=True` is set, and I reproduced the mechanism that forces the marker's removal.** Battery
arm `N14`, re-executed: keying the field rows by index in the export
(`for _i, field in enumerate(self.schema)` / `id=f"insp-field-{_i}"`) produces

```
[XPASS(strict)] F-A: SchemaField.key is interpolat…
1 failed        exit=1
```

`inspector.py` restored, sha256 `2ace7f91d3bdb946 -> 2ace7f91d3bdb946 OK`. **Inc-REPAIR cannot land
the fix without deleting this marker.** The obligation cannot be silently left behind.

**Byte-identity of the four out-of-scope files, against `git archive 954f8f3`, raw bytes:**

| File | sha256 (base = worktree) | Verdict |
|---|---|---|
| `mapper/widgets/inspector.py` | `2ace7f91d3bdb946` | **BYTE-IDENTICAL** |
| `mapper/screens/coverage.py` | `63cf11a4a01b8f8a` | **BYTE-IDENTICAL** |
| `mapper/screens/factory.py` | `771a15e3c418b4c8` | **BYTE-IDENTICAL** |
| `mapper/store.py` | `637d537e7ff2ef0b` | **BYTE-IDENTICAL** |

`git diff 954f8f3` is empty for all four. No seventh source file was taken.

---

## 2 · Did widening the census fixtures close the five F-D gaps?

### **YES — all five, and each kill is by its documented leak oracle.**

I re-ran **all five**, not the three asked for, each against the full default lane, each restored and
proven by sha256:

| # | Mutant | Verdict | Killing arm | Failure mode | Restore |
|---|---|---|---|---|---|
| N9 | `layered.py:520` doc chip — `_fit(doc_txt, …)` -> raw slice | **KILLED** | `test_a89_every_reached_renderer_coerces_what_it_paints` | `assert leaked == []` -> `('LayeredRenderer', (80,24), diff=False, ['0x1','0x200b','0x202c','0x202e','0xe0041'])` | `815a337927e673df` OK |
| N10 | `layered.py:581` ghost title — `_fit(escape(title), …)` -> raw slice | **KILLED** | same arm | `assert leaked == []` -> `(…, diff=True, ['0x1','0x200b','0x202c','0x202e','0xe0041'])` | OK |
| N11 | `layered.py:510` diff chip — `_fit(chip_text, …)` -> `chip_text` | **KILLED** | same arm | `assert leaked == []` -> `(…, diff=True, [same 5])` | OK |
| N12 | `inspector.py:155` attachment chip — `darkside.plain(...)` dropped | **KILLED** | `test_llr_n06_2_3_every_repainted_region_coerces_what_it_paints` | `assert leaked == []` -> `('map-inspector', ['0x1','0x200b','0x202c','0x202e'])` | `2ace7f91d3bdb946` OK |
| N13 | `factory.py:252` tree title — `darkside.plain(...)` dropped | **KILLED** | `test_the_factory_tree_coerces_the_titles_it_paints` | `assert leaked == []` -> `['0x1','0x200b','0x202c','0x202e']` | `771a15e3c418b4c8` OK |

**Every kill is a leak assertion naming the leaked code points. None is a crash-kill, and none is a
golden-digest kill.** I read the assertion text for each rather than inferring it from the arm name.

**The diff-state sweep is real, and the failure text proves it.** N9 fails at `state_diff is not
None == False` while N10 and N11 fail at `True` — so the `A-89` arm genuinely renders with *and*
without a `DiffResult`, which is the non-vacuity guard §12.6 charges `+2` for on the `A-3` pin. That
claim is confirmed by execution.

> One note on N9, so the extra kills are not miscounted as the census working harder than it does:
> my N9 mutant also reddened four `test_c53_legacy_fixture_renders_identically_to_master[layered-…]`
> arms, because a raw slice does not pad where `_fit` does. That is an artifact of how I built the
> mutant, not evidence about coercion. The documented leak oracle is in the kill list independently,
> which is what the claim needed.

**`rail.py:230` is still correctly green, and was not "fixed" into a phantom arm.** Two checks:

- `git diff 954f8f3 -- mapper/widgets/rail.py` is entirely the `collapsed` -> `folded` supersession
  from earlier in Inc-3. Line 230 — `label = darkside.plain(node.ficha.title or nid)` — is
  **untouched**, and no arm was added for it.
- The equivalence holds at the source: `darkside.py:431-433`, `def fit(s, w): s = plain(s)`. Both
  branches at `rail.py:245/247` pass through `darkside.fit(body, RAIL_WIDTH - 4)`, so the coercion
  at 230 is redundant and there is no leak to detect. **Correctly green, correctly left alone.**

---

## 3 · Is the widened `LLR-N06.2.3` census sound?

### **SOUND, and the hostile-key interaction is handled honestly — proven, not argued.**

**The fixture is genuinely widened** (`test_fold.py:256-299`): a two-entry `graph.schema`, a
`fields` dict on every ficha, and two `Attachment`s per ficha with the payload in `kind`/`path`/
`caption`. N12's kill above is the proof that the widening reaches a sink that previously had
nothing standing on it.

**It asserts its input set non-empty before evaluating anything** — five separate guards, all ahead
of the first region read:

```
assert any(ord(c) in banned for c in graph.nodes["b0"].ficha.title)   # payload is in range
assert graph.schema                                                   # inspector paints field rows
assert graph.nodes["b0"].ficha.attachments                            # the chip is reached
assert any(ord(c) in banned for a in …attachments for c in a.caption + a.path + a.kind)
assert any(ord(c) in banned for sf in graph.schema for c in sf.label)
```

plus `assert len(screen.graph.nodes) == 7` (the round trip survived) and `assert "map-minimap" in
regions` / `assert len(regions) >= 4` / `assert checked == len(regions)` on the derived region set.

**The survival assertion is present and correctly placed** — `assert app.is_running` at
`test_fold.py:404`, **before** any region is read, with a second at `:461` after the frame sweep.

**The schema keys are identifier-safe** (`"D"`, `"obs"`), and the bound is recorded in the fixture's
own docstring rather than left implicit.

**The interaction the author flags is the decisive question, so I tested it rather than accepting the
reasoning.** I planted `"D" + chr(0x01)` as the census fixture's own schema key and ran the arm:

```
exit=1  ->  RED
tests/test_fold.py restored: sha256 eb21478973a72c80 -> eb21478973a72c80 OK
```

**The arm goes red, not green-on-nothing.** This is the honest outcome: the failure mode the author
warns about — "a census that reports nothing while looking green" — **cannot occur**, because the
survival assertion and the crash together make the degenerate case loud. The decision to keep the
keys safe here and carry the hostile-key obligation in the strict-xfail arm instead is correct, and
it is correct for a reason that is now measured.

**One clarification so the brief's checklist is not read as a gap.** The brief asks that this census
carry "schema, fields, attachments and a diff". It carries the first three. It does **not** carry a
`DiffResult`, and it should not: a diff is `ViewState`, not `Graph`, and `MapScreen` with no diff
active has none — driving one here would be testing a state the screen is not in. The diff-state
coverage lives in the `A-89` census, where N10/N11 confirmed above that **both** diff states are
swept. The placement is right.

---

## 4 · The two claims the routing rests on

### 4a · F-A is pre-existing at `954f8f3` — **CONFIRMED**

Reproduced on a clean `git archive 954f8f3` export (`open_map` inlined, because
`tests/inc3_support.py` does not exist at that commit), same probe, same six keys:

| Key | `954f8f3` | post-fix tree |
|---|---|---|
| `chr(0x01)` | `running=False`, `BadIdentifier` | `running=False`, `BadIdentifier` |
| `"a" + chr(0xF1) + "o"` | `running=False`, `BadIdentifier` | `running=False`, `BadIdentifier` |
| `"fecha" + chr(0x20) + "limite"` | `running=False`, `BadIdentifier` | `running=False`, `BadIdentifier` |
| `chr(0x202E)` | `running=False`, `BadIdentifier` | `running=False`, `BadIdentifier` |
| `chr(0x200B)` | `running=False`, `BadIdentifier` | `running=False`, `BadIdentifier` |
| **control** `"obs"` | `running=True` | `running=True` |

**Identical on both trees. It is pre-existing, not a regression.** Inc-3 neither caused it nor made
it worse.

### 4b · F-A subsumes `SEC-F1`'s attack — **CONFIRMED**

Driven end to end: save a map whose ficha titles *and* schema labels carry the payload, open it,
press `e` (`action_export_svg`), then inspect the store directory for written SVGs.

| Schema key | alive after `e` | exception | SVG written |
|---|---|---|---|
| `chr(0x01)` | **False** | `BadIdentifier` | **`[]`** |
| `chr(0x202E)` | **False** | `BadIdentifier` | **`[]`** |
| `"a" + chr(0xF1) + "o"` | **False** | `BadIdentifier` | **`[]`** |
| **control** `"obs"` | True | none | `['sub.svg']` |

**A hostile `SchemaField.key` cannot reach the SVG sink at all — the session is gone first.** The
control proves the probe can produce an SVG when the key is benign, so the empty result is
subsumption and not a broken probe.

**Both premises hold, so the routing decision was correct.** F-A is a pre-existing crash that
strictly dominates the leak `SEC-F1` closed; deferring the fix to Inc-REPAIR does not leave a
reachable leak open, because the leak is unreachable while the crash stands. The `layered.py:473`
coercion remains correct defence in depth.

---

## 5 · New surface from round 2 only

### **CLEAN. No new leak, no new unguarded pump path, no new external surface.**

**`_header_line` / `header_rows` (`layered.py:362-441`) carry no file-derived text.** The line is
built from `len(graph.nodes)`, a coverage percentage, `bool(graph.schema)`, `OVERFLOW_TOKEN` and
fixed Spanish literals. No node id, no ficha title, meta, notes, fields, attachment or schema key
reaches it. `header_rows` is a module-level pure function — no I/O, no subprocess, no network. **The
extraction adds no sink.**

**`_declare_after_layout` does not escape the message pump.** It is scheduled by
`call_after_refresh` (`app.py:1228`), where an escape is fatal, so I drove it directly against both
hostile graph shapes this batch guards for:

| Graph | `refresh_canvas` | `_declare_after_layout` | `_canvas_size` | `app.is_running` |
|---|---|---|---|---|
| cycle (`root -> a -> b -> a`) | ok | **ok** | ok | True |
| dangling edge (`root -> fantasma`) | ok | **ok** | ok | True |

Its renderer call is inside `try/except Exception`, and its one unguarded tail —
`query_one("#map-pagination").update(self._pagination_text())` — is safe because `_pagination_text`
reaches `_unpainted_ids`, which carries its own `try/except -> None` (the guard placement the
previous pass proved load-bearing with M-K). **No new fatal path.**

**`_minimap_text` guard is present and correctly shaped** — `app.py`, `try: minimap =
self._minimap_text() / except Exception: minimap = darkside.Text("")`, degrading to empty rather
than escaping.

**Edge-hint clearing introduces no sink** — `set_hint("")` on success, `set_hint("borde del
territorio")` otherwise. Both constants; no file-derived text.

**Standard sweep on the full diff vs `954f8f3`:**

| Check | Result |
|---|---|
| Secrets / API keys / tokens / `.env` / private keys / bearer tokens | **0** |
| Absolute paths / Windows username / emails | **0** — `F-F` is **closed**, verified over every added line |
| New dependency | **none**; `pyproject.toml` untouched (`git diff --stat` empty) |
| New network surface | **none** |
| New process surface | `subprocess.run(["git","ls-files",*globs], cwd=REPO, capture_output=True, text=True, check=True)` in two test helpers — fixed argv, **no `shell=True`**, call-site-literal globs, `cwd` pinned, test-only. **Acceptable** |
| `eval` / `exec` / `pickle` / `__import__` added | **0** |
| Destructive filesystem calls added | **0** |
| LFPDPPP / client-data exposure | **none** — no client data in the diff, nothing leaves the machine |

### F-E — the fix is real, and the scan asserts a non-empty input set

**Both prior-batch artifacts are clean.** Independent scan against `darkside.COERCION_RANGES`:

```
.dev-flow/2026-08-25-ui-next-batch-01/02b-security-review.md                     CLEAN
.dev-flow/…/increment-001-code-review-confirmation.md                            CLEAN
whole-repo scan, 176 files (mapper/ + tests/ + .dev-flow/ + fixtures/ + maps/):  OFFENDERS: none
```

**The scan is genuinely extended to the artifact tree** (`test_fold.py:212-216`, `rglob` over
`.dev-flow` for `*.md` and `*.json`), and the choice of `rglob` over `git ls-files` for that half is
right for the stated reason: an increment's own artifacts are untracked while it is writing them.

**It asserts a non-empty input set on both halves** — `assert len(artifacts) > 20` and
`assert len(sources) > 30`. It is not a guard that passes by finding nothing to look at.

Two residuals on this guard follow as `P3-F1` and `P3-F2`.

---

## Findings

### P3-F1 — the artifact scan's non-vacuity clause goes red the moment this batch is committed  [Severity: **MEDIUM**]

- **What:** `test_no_tracked_file_spells_a_coerced_code_point_INCLUDING_the_artifacts` asserts that
  the `rglob` view is a **strict** superset of the `git ls-files` view:
  `assert not set(artifacts) <= set(_tracked(".dev-flow/*.md", ".dev-flow/**/*.md", ".dev-flow/*.json"))`,
  with the message *"no untracked artifact is in scope; the rglob is buying nothing today"*. The
  clause is satisfied **only while some `.dev-flow` artifact is untracked**. It is green right now
  purely because five artifacts happen to be untracked in the working tree.
- **Where:** `tests/test_fold.py:223-225`.
- **Why it matters:** measured, not predicted. My first export baseline — a faithful copy of the
  working tree with `git add -A`, i.e. exactly the post-commit tracking state — failed with
  `1 failed, 795 passed, 17 deselected, 1 xfailed`, **exit 1**, at that assertion and no other.
  Re-running the same tree with the five artifacts un-staged gives `796 passed … exit 0`. So this
  increment **cannot be committed in full without turning its own new guard red**, and the natural
  reaction to a red non-vacuity clause is to weaken or delete it — which loses the widening that
  `F-E` was raised for. The security property the arm enforces is sound; its self-check is coupled
  to repository state that is about to change.
- **Recommendation:** replace the tracking-state comparison with one that does not depend on what is
  committed. Assert the instrument instead of today's delta — e.g. keep the `rglob` and assert the
  *pattern set* is wider (`.dev-flow` is swept at all, and `_tracked` is not consulted for that
  half), or drive it with a temporary untracked file the arm creates and removes:

  ```python
  # the rglob really does see untracked artifacts, asserted by construction
  probe = REPO / ".dev-flow" / "_scan_probe.md"
  probe.write_text("ok", encoding="utf-8")
  try:
      seen = {str(p.relative_to(REPO)).replace("\\", "/")
              for p in (REPO / ".dev-flow").rglob("*.md")}
      assert ".dev-flow/_scan_probe.md" in seen, (
          "the rglob does not see untracked artifacts; it is the tracked "
          "sweep wearing a different instrument"
      )
  finally:
      probe.unlink()
  ```

  Land it in the same commit as the increment, or the batch lands red.

### P3-F2 — the "extended" scan still does not sweep the directory its own docstring cites  [Severity: LOW]

- **What:** the scan covers `mapper/`, `tests/` and `.dev-flow/`. It does **not** cover `fixtures/`
  or `maps/` — the directories holding the `.mmd` / `.yml` map data the product actually loads. The
  arm's docstring motivates itself with *"batch 1 shipped a literal backspace in a fixture and the
  resulting test passed on everything"*, so a reader would reasonably believe fixtures are in scope.
- **Where:** `tests/test_fold.py:211-216` — the source half is `_tracked("mapper/*.py",
  "mapper/**/*.py", "tests/*.py", "tests/**/*.py")`; the artifact half is `.dev-flow` only.
- **Why it matters:** measured. I planted `chr(0x200B)` in `fixtures/anidado.mmd` (new in this
  increment) and in `maps/legacy.mmd`, and ran the arm:

  | Planted in | Arm exit | Verdict |
  |---|---|---|
  | `fixtures/anidado.mmd` | **0** | **NOT CAUGHT** |
  | `maps/legacy.mmd` | **0** | **NOT CAUGHT** |

  Both files restored, sha256 `d1be5a2c82378f50` and `1fcc9a644e7b4c5e`, `OK`. This is not a live
  leak — I verified independently that both trees are clean today (176 files, zero offenders) — but
  the guard against the *original* defect class is still absent. Low blast radius: a fixture code
  point is a test-hygiene problem, not an operator-facing one.
- **Recommendation:** add `fixtures/*`, `fixtures/**/*`, `maps/*`, `maps/**/*` to the source half's
  glob list, and assert that half non-empty too. One line, and it closes the case the docstring
  already argues for.

### P3-F3 — the F-A arm exercises only its first key at run time  [Severity: LOW]

- **What:** `test_f_a_a_map_whose_schema_keys_are_not_identifiers_still_opens` loops over three keys,
  but the first iteration (`chr(0x01)`) raises `BadIdentifier`, so `"a" + chr(0xF1) + "o"` and
  `"fecha" + chr(0x20) + "limite"` are never driven. The docstring narrates *"6 of 6 keys"*, which
  is a prior measurement the arm does not re-execute.
- **Where:** `tests/test_fold.py:561-579`.
- **Why it matters:** small, and **it does not weaken the routing** — I confirmed each of the three
  keys crashes independently (§1), and the loop ordering is actually safe under strict xfail: the
  arm cannot XPASS until *every* key passes, so a partial fix in Inc-REPAIR keeps it xfailing rather
  than falsely reporting closure. The finding is only that the arm proves less at run time than it
  reads as proving, which matters when the next reviewer treats the docstring as evidence.
- **Recommendation:** either parametrise over the three keys so each is its own arm and each is its
  own xfail, or soften the docstring to say the loop short-circuits by design and cite where the
  6-of-6 measurement lives.

### P3-F4 — stray untracked directory at the repository root  [Severity: LOW]

- **What / where:** an empty directory literally named `--help` sits at the repo root, dated
  2026-08-24 — debris from a mis-typed command, **pre-existing** and not from this increment.
- **Why it matters:** essentially nothing. It is empty, so git will not commit it, and it is
  untracked. Noted only so it is not rediscovered as a mystery. A directory named like a CLI flag can
  confuse shell globbing in future tooling.
- **Recommendation:** remove it when convenient. Not a gate item.

---

## Verdict

- [x] **OK to ship** — 0 HIGH. F-A is correctly routed to Inc-REPAIR with the obligation landed and
      mechanically enforced.
- [ ] OK to ship with the listed mitigations applied first
- [ ] Block

**Safe to commit with F-A routed rather than fixed: YES.** The routing does not leave a reachable
leak open — F-A subsumes `SEC-F1`'s attack, so the hardened SVG sink is unreachable by that path
anyway, and F-A is pre-existing rather than introduced. The strict-xfail arm cannot be lost between
increments; I reproduced the `XPASS(strict) -> FAILED` mechanism directly.

**Fix `P3-F1` in the same commit.** It is not a security block — it is a commit-mechanics defect, and
it is the one thing here that is certain to bite: the batch's own new guard fails on the tree it is
about to become. `P3-F2`, `P3-F3`, `P3-F4` are LOW and belong with the Inc-REPAIR work.

**Carried unchanged from the previous pass, still open, still correctly routed:** `F-A` (HIGH, to
Inc-REPAIR), `F-B`, `F-C` (MEDIUM, `escape`-only sinks on `coverage.py` / `factory.py`), `F-G`
(part-closed), `F-H`, and the new `OutlineRail.render` carry.

---

## Evidence checklist

- [x] Each finding has what · where · why · recommendation — `P3-F1` … `P3-F4`, all four fields.
- [x] Each finding has a severity rating — **0 HIGH**, 1 MEDIUM, 3 LOW.
- [x] No secret values appear in this output — none were found; none reproduced.
- [x] No banned code point is spelled into this file — every payload named by code point
      (`chr(0x01)`, `chr(0xF1)`, `U+200B`, …); every probe built them with `chr(0x…)` at run time.
- [x] Verdict is explicit — **SIGN-OFF**, with the one must-fix-before-commit item named.
- [x] New tool/integration scope and blast radius addressed — **no new MCP / Composio / n8n /
      network / dependency surface**; `pyproject.toml` untouched. The only process call is
      `git ls-files` with fixed argv, no shell, pinned `cwd`, test-only.
- [x] Tree integrity proven by sha256 — six unchanged product files match the previous pass's
      digests exactly; only `app.py` and `layered.py` moved; **12 of 12 mutation restores `OK`**;
      `git status` identical to session start.

---

*Scoped confirmation pass, questions 1–5 only. Every claim above was re-executed in a `tar` export
with its own `git init`, plus a `git archive 954f8f3` export for the pre-existence reproduction. 12
mutants applied (5 × F-D, 1 × census hostile key, 2 × scan coverage, 1 × N14 F-A-fixed, 3 restored
baselines), 12 killed or resolved as intended, 12 of 12 restores `OK`. Default lane `796 passed, 17
deselected, 1 xfailed`, slow lane `17 passed, 797 deselected`, both exit 0.*
